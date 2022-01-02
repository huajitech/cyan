from typing import Any
from httpx import AsyncClient

from cyan.model.member import Member
from cyan import Session


class Guild:
    """
    频道。
    """

    _props: dict[str, Any]
    _session: Session

    def __init__(self, session: Session, props: dict[str, Any]):
        """
        初始化 `Guild` 实例。

        参数：
            - props: 属性
        """

        self._props = props
        self._session = session

    @property
    def identifier(self) -> str:
        """
        频道 ID。
        """

        return self._props["id"]

    @property
    def name(self) -> str:
        """
        频道名。
        """

        return self._props["name"]

    @property
    def capacity(self) -> int:
        """
        频道最大成员数。
        """

        return self._props["max_members"]

    @property
    def description(self) -> str:
        """
        频道描述。
        """

        return self._props["description"]

    async def get_icon(self):
        """
        异步获取频道头像。

        返回：
            以 `bytes` 类型表示的图像文件内容。
        """

        client = AsyncClient()
        response = await client.get(self._props["icon"])  # type: ignore
        return response.content

    async def get_members(self):
        """
        异步获取当前频道的所有成员。

        返回：
            以 `Member` 类型表示成员的 `list[T]` 集合。
        """

        content = await self._session.get(f"/guilds/{self.identifier}/members")
        return list(map(Member, content))
