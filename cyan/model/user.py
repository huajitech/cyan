from typing import Any
from httpx import AsyncClient


class User:
    """
    用户。
    """

    _props: dict[str, Any]

    def __init__(self, props: dict[str, Any]):
        """
        初始化 `User` 实例。

        参数：
            - props: 属性
        """

        self._props = props

    @property
    def identifier(self) -> str:
        """
        用户 ID。
        """

        return self._props["id"]

    @property
    def name(self) -> str:
        """
        用户名。
        """

        return self._props["username"]

    @property
    def bot(self) -> bool:
        """
        用户是否为机器人。
        """

        return self._props["bot"]

    async def get_avatar(self):
        """
        异步获取用户头像。

        返回：
            以 `bytes` 类型表示的图像文件内容。
        """

        client = AsyncClient()
        response = await client.get(self._props["avatar"])  # type: ignore
        return response.content
