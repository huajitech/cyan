import asyncio
from asyncio.tasks import Task
import inspect
import json
from enum import Enum
from abc import abstractmethod, abstractstaticmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, NoReturn
from websockets.client import connect
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


class Intent(Enum):
    """
    `Intent`
    """
    DEFAULT = 0
    GUILD = 1 << 0
    MEMBER = 1 << 1
    GUILD_MESSAGE = 1 << 10
    DIRECT_MESSAGE = 1 << 12
    MESSAGE_AUDIT = 1 << 27
    FORUM = 1 << 28
    VOICE = 1 << 29
    MENTION = 1 << 30


class EventType:
    _name: str
    _intent: Intent

    def __init__(self, name: str, intent: Intent):
        self._name = name
        self._intent = intent

    @property
    def name(self):
        return self._name

    @property
    def intent(self):
        return self._intent


class Event:
    _handlers: set[EventHandler]
    _bot: "Bot"

    def __init__(self, bot: "Bot"):
        self._handlers = set[EventHandler]()
        self._bot = bot

    @abstractstaticmethod
    def get_event_type() -> EventType:
        raise NotImplementedError

    @abstractmethod
    def _parse_data(self, data: Any) -> Any:
        raise NotImplementedError

    def bind(self, handler: EventHandler):
        self._handlers.add(handler)

    def handle(self):
        def _decorate(func: EventHandler):
            self._handlers.add(func)

        return _decorate

    async def distribute(self, data: Any):
        event_data = self._parse_data(data)
        for handler in self._handlers:
            args = {"bot": self._bot, "data": event_data}
            argnames = inspect.signature(handler).parameters.keys()
            await handler(**{
                name: value for name, value in args.items() if name in argnames  # type: ignore
            })


class Operation(Enum):
    EVENT = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    RESUME = 6
    RECONNECT = 7
    INVALID_SESSION = 9
    CONNECTED = 10
    HEARTBEAT_RECEIVED = 11


class EventSource:
    _websocket: WebSocketClientProtocol
    _bot: "Bot"
    _serial_code: int
    _events: set[Event]
    _session: str | None
    _authorization: str
    _connected: bool
    _heartbeat_task: Task[NoReturn] | None

    def __init__(self, bot: "Bot", authorization: str):
        self._websocket = WebSocketClientProtocol()
        self._bot = bot
        self._serial_code = -1
        self._events = set[Event]()
        self._session = None
        self._authorization = authorization
        self._connected = False
        self._heartbeat_task = None

    @property
    def bot(self):
        return self._bot

    @property
    def connected(self):
        return self._connected and not self._websocket.closed

    async def connect(self):
        response = await self.bot.get("/gateway")
        content = response.json()
        self._websocket = await connect(content["url"])
        self._connected = True
        asyncio.create_task(self._receive())

    async def disconnect(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        await self._websocket.close()
        self._session = None
        self._serial_code = -1
        self._connected = False

    async def send(self, opcode: Operation, payload: Any = None):
        content = {"op": opcode.value}
        content.update({"d": payload} if payload else {})
        data = json.dumps(content)
        await self._websocket.send(data)

    def get_event(self, _type: type[Event]):
        for event in self._events:
            if isinstance(event, _type):
                return event
        event = _type(self._bot)
        self._events.add(event)
        if self.connected:
            intent = _type.get_event_type().intent
            for registered_event in self._events:
                if registered_event.get_event_type().intent == intent:
                    return event
            raise InvalidOperationError("WebSocket 已连接时不可获取未订阅 Intent 的事件。")
        return event

    def listen(self, _type: type[Event]):
        return self.get_event(_type).handle()

    def _calculate_intents(self):
        intents = set(event.get_event_type().intent for event in self._events)
        intents_number = 0
        for intent in intents:
            intents_number |= intent.value
        return intents_number

    async def _resume(self):
        payload = {
            "token": self._authorization,
            "session_id": self._session,
            "seq": self._serial_code
        }
        await self.send(Operation.RESUME, payload)

    async def _identify(self):
        from cyan.event.events._connection import ReadyEvent

        self.get_event(ReadyEvent).bind(self._on_ready)
        payload = {
            "token": self._authorization,
            "intents": self._calculate_intents(),
            "properties": dict[str, Any]()
        }
        await self.send(Operation.IDENTIFY, payload)

    async def _on_ready(self, data: "ReadyEventData"):
        self._session = data.session

    async def _receive(self):
        async for data in self._websocket:
            content = json.loads(data)
            await self._handle(content)

    async def _call_events(self, event_type: str, data: Any):
        for event in self._events:
            if event.get_event_type().name == event_type:
                await event.distribute(data)

    async def _send_heartbeat(self):
        await self.send(Operation.HEARTBEAT, self._serial_code)

    async def _heartbeat(self, interval: int):
        while True:
            await asyncio.sleep(interval / 1000)
            await self._send_heartbeat()

    def _set_heartbeat(self, interval: int):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(self._heartbeat(interval))

    async def _handle(self, content: dict[str, Any]):
        operation = Operation(content["op"])
        self._serial_code = content.get("s", self._serial_code)
        match operation:
            case Operation.EVENT:
                await self._call_events(content["t"], content["d"])
            case Operation.RECONNECT:
                await self._resume()
            case Operation.CONNECTED:
                self._set_heartbeat(content["d"]["heartbeat_interval"])
                await self._identify()
            case Operation.HEARTBEAT:
                await self._send_heartbeat()
