import asyncio
import inspect
import json
import warnings
from asyncio.tasks import Task
from enum import Enum
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, NoReturn
from websockets.client import connect
from websockets.exceptions import ConnectionClosed
from websockets.legacy.client import WebSocketClientProtocol

from cyan.exception import InvalidOperationError


if TYPE_CHECKING:
    from cyan.event.events._connection import ReadyEventData
    from cyan.bot import Bot


EventHandler = (
    Callable[
        [Any], Awaitable[None] | Awaitable[NoReturn]
    ] | Callable[
        [Any, Any], Awaitable[None] | Awaitable[NoReturn]
    ]
)
"""
事件处理器。
"""


class NotSupported(Exception):
    """
    当操作不支持时抛出。
    """

    pass


class Intent(Enum):
    """
    事件注册 `Intent`。
    """

    DEFAULT = 0
    """
    默认。
    """

    GUILD = 1 << 0
    """
    频道事件。
    """

    MEMBER = 1 << 1
    """
    成员事件。
    """

    GUILD_EXPRESSION = 1 << 10
    """
    频道表态事件。
    """

    DIRECT_MESSAGE = 1 << 12
    """
    直接消息事件。
    """

    MESSAGE_AUDIT = 1 << 27
    """
    消息审核事件。
    """

    FORUM = 1 << 28
    """
    论坛事件。
    """

    VOICE = 1 << 29
    """
    语音事件。
    """

    MENTION = 1 << 30
    """
    提及机器人事件。
    """


class EventInfo:
    """
    事件信息。
    """

    _name: str
    _intent: Intent

    def __init__(self, name: str, intent: Intent) -> None:
        self._name = name
        self._intent = intent

    @property
    def name(self) -> str:
        """
        事件名称。
        """

        return self._name

    @property
    def intent(self) -> Intent:
        """
        事件所需注册 `Intent`。
        """

        return self._intent


class Event:
    _handlers: set[EventHandler]
    _bot: "Bot"

    def __init__(self, bot: "Bot") -> None:
        self._handlers = set[EventHandler]()
        self._bot = bot

    @staticmethod
    @abstractmethod
    def get_event_info() -> EventInfo:
        """
        获取当前事件信息。

        返回：
            以 `EventInfo` 类型表示的事件信息。
        """

        raise NotImplementedError

    @abstractmethod
    async def _parse_data(self, data: Any) -> Any:
        """
        解析数据。

        参数：
            - data: 将要解析的数据

        返回：
            解析后的数据。
        """

        raise NotImplementedError

    def bind(self, *handler: EventHandler) -> None:
        """
        绑定事件处理器。

        参数：
            - handler: 将要绑定的事件处理器
        """

        self._handlers.update(handler)

    def handle(self) -> Callable[[EventHandler], None]:
        """
        装饰事件处理器以绑定至当前事件。
        """

        def _decorate(func: EventHandler):
            self.bind(func)

        return _decorate

    async def distribute(self, data: Any) -> None:
        """
        分发事件数据。

        参数：
            - data: 用于解析及分发的数据
        """

        try:
            event_data = await self._parse_data(data)
        except NotSupported:
            return
        except Exception:
            raise
        for handler in self._handlers:
            args = {"bot": self._bot, "data": event_data}
            argnames = inspect.signature(handler).parameters.keys()
            try:
                await handler(**{
                    name: value for name, value in args.items() if name in argnames  # type: ignore
                })
            except Exception as ex:
                message = str(ex)
                warnings.warn(
                    f"调用事件处理器 {handler} 时捕获到异常 {type(ex).__name__}" + (
                        ":\n" + message if message else "。"
                    )
                )


class Operation(Enum):
    """
    操作。
    """

    EVENT = 0
    """
    事件。
    """

    HEARTBEAT = 1
    """
    心跳包。
    """

    IDENTIFY = 2
    """
    认证。
    """

    RESUME = 6
    """
    恢复。
    """

    RECONNECT = 7
    """
    重新连接。
    """

    INVALID_SESSION = 9
    """
    无效会话。
    """

    CONNECTED = 10
    """
    已连接。
    """

    HEARTBEAT_RECEIVED = 11
    """
    已接收心跳包。
    """


class _EventProvider:
    _type_dict: dict[type, Event]
    _event_name_dict: dict[str, set[Event]]
    _registered_intents: set[Intent]

    def __init__(self) -> None:
        self._type_dict = dict[type, Event]()
        self._event_name_dict = dict[str, set[Event]]()
        self._registered_intents = set[Intent]((Intent.DEFAULT,))

    def get_intents(self) -> set[Intent]:
        return self._registered_intents

    def get_by_type(self, bot: "Bot", _type: type[Event]) -> Event:
        event = self._type_dict.get(_type, None)
        if event:
            return event
        event = _type(bot)
        self._type_dict[_type] = event
        event_info = _type.get_event_info()
        events = self._event_name_dict.get(event_info.name, None)
        if not events:
            self._event_name_dict[event_info.name] = events = set[Event]()
        events.add(event)
        self._registered_intents.add(event_info.intent)
        return event

    def get_by_event_name(self, event_name: str) -> set[Event]:
        return self._event_name_dict.get(event_name, set[Event]())


class _ConnectionResumed(Exception):
    pass


class EventSource:
    """
    事件源。
    """

    _websocket: WebSocketClientProtocol
    _bot: "Bot"
    _serial_code: int
    _session: str | None
    _authorization: str
    _connected: bool
    _heartbeat_task: Task[NoReturn] | None
    _event_provider: _EventProvider
    _task: Task[None] | None

    def __init__(self, bot: "Bot", authorization: str):
        self._websocket = WebSocketClientProtocol()
        self._bot = bot
        self._serial_code = -1
        self._session = None
        self._authorization = authorization
        self._connected = False
        self._heartbeat_task = None
        self._event_provider = _EventProvider()
        self._task = None

    @property
    def bot(self) -> "Bot":
        """
        事件源所属机器人实例。
        """

        return self._bot

    @property
    def connected(self) -> bool:
        """
        `WebSocket` 是否已连接。
        """

        return self._connected

    async def connect(self) -> None:
        """
        异步连接服务器。
        """

        if self.connected:
            raise InvalidOperationError("已连接至服务器。")
        await self._connect()
        await self._identify()

    async def _connect(self) -> None:
        response = await self.bot.get("/gateway")
        content = response.json()
        self._websocket = await connect(content["url"])
        self._connected = True
        self._task = asyncio.create_task(self._receive())

    async def disconnect(self) -> None:
        """
        异步断开连接。
        """

        if not self.connected:
            raise InvalidOperationError("未连接至服务器。")
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._task:
            self._task.cancel()
        await self._websocket.close()
        self._session = None
        self._serial_code = -1
        self._connected = False

    async def send(self, operation: Operation, payload: Any = None) -> None:
        """
        异步发送数据至服务器。

        参数：
            - operation: 操作
            - payload: Payload
        """

        content = {"op": operation.value}
        if payload:
            content["d"] = payload
        data = json.dumps(content)
        await self._websocket.send(data)

    def get_event(self, _type: type[Event]) -> Event:
        """
        获取指定类型的事件。

        参数：
            - _type: 所需获取事件的类型

        返回：
            指定类型事件的实例。
        """

        if (
            self.connected and _type.get_event_info()
            .intent not in self._event_provider.get_intents()
        ):
            raise InvalidOperationError("WebSocket 已连接时不可获取未订阅 Intent 的事件。")
        return self._event_provider.get_by_type(self._bot, _type)

    def listen(self, _type: type[Event]) -> Callable[[EventHandler], None]:
        """
        装饰事件处理器以监听指定事件。

        参数：
            - _type: 所需监听事件的类型
        """

        return self.get_event(_type).handle()

    async def wait_until_stopped(self) -> None:
        """
        异步等待至事件源停止接收消息。
        """

        while True:
            if self._task:
                try:
                    await self._task
                except _ConnectionResumed:
                    continue
            return

    def _calculate_intents(self) -> int:
        intents = self._event_provider.get_intents()
        intents_number = 0
        for intent in intents:
            intents_number |= intent.value
        return intents_number

    async def _resume(self) -> None:
        payload = {
            "token": self._authorization,
            "session_id": self._session,
            "seq": self._serial_code
        }
        await self.send(Operation.RESUME, payload)

    async def _identify(self) -> None:
        from cyan.event.events._connection import ReadyEvent

        self.get_event(ReadyEvent).bind(self._on_ready)
        payload = {
            "token": self._authorization,
            "intents": self._calculate_intents(),
            "properties": dict[str, Any]()
        }
        await self.send(Operation.IDENTIFY, payload)

    async def _on_ready(self, data: "ReadyEventData") -> None:
        self._session = data.session

    async def _receive(self) -> None:
        async for data in self._websocket:
            try:
                content = json.loads(data)
                await self._handle(content)
            except ConnectionClosed as ex:
                if ex.code != 4009:
                    raise
                await self._connect()
                try:
                    await self._resume()
                except ConnectionClosed as ex:
                    if ex.code != 4009:
                        raise
                    await self.connect()
                raise _ConnectionResumed

    async def _call_events(self, event_name: str, data: Any) -> None:
        for event in self._event_provider.get_by_event_name(event_name):
            if event.get_event_info().name == event_name:
                await event.distribute(data)

    async def _send_heartbeat(self) -> None:
        await self.send(Operation.HEARTBEAT, self._serial_code)

    def _set_heartbeat(self, interval: int) -> None:
        async def _heartbeat():
            while True:
                await asyncio.sleep(interval / 1000)
                await self._send_heartbeat()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(_heartbeat())

    async def _handle(self, content: dict[str, Any]) -> None:
        operation = Operation(content["op"])
        self._serial_code = content.get("s", self._serial_code)
        match operation:
            case Operation.EVENT:
                await self._call_events(content["t"], content["d"])
            case Operation.RECONNECT:
                await self._resume()
            case Operation.CONNECTED:
                self._set_heartbeat(content["d"]["heartbeat_interval"])
            case Operation.HEARTBEAT:
                await self._send_heartbeat()
