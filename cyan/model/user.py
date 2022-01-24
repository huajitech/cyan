from typing import Any
from httpx import AsyncClient

from cyan.bot import Bot
from cyan.model import Model


class User(Model):
    """
    用户。
    """

    _props: dict[str, Any]
    _bot: Bot

    def __init__(self, bot: Bot, props: dict[str, Any]) -> None:
        """
        初始化 `User` 实例。

        参数：
            - bot: 用户所属机器人
            - props: 属性
        """

        self._props = props
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["id"]

    @property
    def name(self) -> str:
        """
        用户名称。
        """

        return self._props["username"]

    @property
    def is_bot(self) -> bool:
        """
        用户是否为机器人。
        """

        return self._props["bot"]

    async def get_avatar(self) -> bytes:
        """
        异步获取用户头像。

        返回：
            以 `bytes` 类型表示的图像文件内容。
        """

        client = AsyncClient()
        response = await client.get(self._props["avatar"])  # type: ignore
        return response.content
