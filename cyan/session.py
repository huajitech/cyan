import asyncio
import traceback
import warnings
from typing import Awaitable, Callable, NoReturn, Optional, Set, Type

from cyan.bot import Bot, Ticket
from cyan.event import Event, EventHandler


BotStartedHandler = Callable[[Bot], Awaitable[Optional[NoReturn]]]
"""
机器人启动事件处理器。
"""


class Session:
    """
    会话。
    """

    _bot: Bot
    _started_handlers: Set[BotStartedHandler]

    def __init__(self, api_base_url: str, ticket: Ticket) -> None:
        """
        初始化 `Session` 示例。

        参数：
            - api_base_url: API 地址（包括 schema, host, port）
            - ticket: 票据
        """

        self._bot = Bot(api_base_url, ticket)
        self._started_handlers = set()

    def on_started(self, func: BotStartedHandler) -> BotStartedHandler:
        """
        装饰事件处理器以监听机器人启动事件。
        """

        self._started_handlers.add(func)
        return func

    def on(self, _type: Type[Event]) -> Callable[[EventHandler], None]:
        """
        装饰事件处理器以监听指定事件。

        参数：
            - _type: 所需监听事件的类型
        """

        return self._bot.event_source.listen(_type)

    def run(self) -> None:
        """
        运行当前会话。
        """

        asyncio.run(self._run())

    async def _run(self) -> None:
        async with self._bot as bot:
            source = bot.event_source
            await source.connect()
            for handler in self._started_handlers:
                try:
                    await handler(bot)
                except Exception:
                    warnings.warn(f"调用事件处理器 {handler} 时捕获到异常:\n{traceback.format_exc()}")
            await source.wait_until_stopped()
