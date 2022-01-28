import asyncio
import traceback
import warnings
from typing import Awaitable, Callable, NoReturn, Optional, Set, Type

from cyan.bot import Bot, Ticket
from cyan.event import Event, EventHandler


SessionHandler = Callable[[Bot], Awaitable[Optional[NoReturn]]]
"""
机器人事件处理器。
"""


class Session:
    """
    会话。
    """

    _bot: Bot
    _started_handlers: Set[SessionHandler]
    _terminated_handlers: Set[SessionHandler]

    def __init__(self, api_base_url: str, ticket: Ticket) -> None:
        """
        初始化 `Session` 示例。

        参数:
            - api_base_url: API 地址（包括 schema, host, port）
            - ticket: 票据
        """

        self._bot = Bot(api_base_url, ticket)
        self._started_handlers = set()
        self._terminated_handlers = set()

    def on_started(self, func: SessionHandler) -> SessionHandler:
        """
        装饰事件处理器以监听会话启动事件。
        """

        self._started_handlers.add(func)
        return func

    def on_terminated(self, func: SessionHandler) -> SessionHandler:
        """
        装饰事件处理器以监听会话结束事件。
        """

        self._terminated_handlers.add(func)
        return func

    def on(self, _type: Type[Event]) -> Callable[[EventHandler], None]:
        """
        装饰事件处理器以监听指定事件。

        参数:
            - _type: 所需监听事件的类型
        """

        return self._bot.event_source.listen(_type)

    def run(self) -> None:
        """
        运行当前会话。
        """

        asyncio.run(self._run())

    async def _distribute(self, handlers: Set[SessionHandler]):
        for handler in handlers:
            try:
                await handler(self._bot)
            except Exception:
                warnings.warn(f"调用事件处理器 {handler} 时捕获到异常:\n{traceback.format_exc()}")

    async def _run(self) -> None:
        async with self._bot:
            await self._distribute(self._started_handlers)
            source = self._bot.event_source
            try:
                await source.connect()
                await source.wait_until_stopped()
            except Exception:
                warnings.warn(f"会话由于异常意外结束:\n{traceback.format_exc()}")
            await self._distribute(self._terminated_handlers)
