from typing import Any
from httpx import AsyncClient

from cyan.constant import MEMBER_QUERY_LIMIT
from cyan.exception import OpenApiError
from cyan.session import Session
from cyan.model.channel import Channel, ChannelGroup, parse as channel_parse
from cyan.model.member import Member


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
            - session: 会话
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

        return self._props.get("max_members", -1)

    @property
    def description(self) -> str:
        """
        频道描述。
        """

        return self._props.get("description", "")

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
            以 `Member` 类型表示成员的 `list` 集合。
        """

        cur = None
        members = list[Member]()
        while True:
            params: dict[str, Any] = {"limit": MEMBER_QUERY_LIMIT}
            params.update(
                {"after": cur} if cur else {}
            )
            try:
                content = await self._session.get(
                    f"/guilds/{self.identifier}/members",
                    params
                )
                members.extend(map(Member, content))
                if len(content) < MEMBER_QUERY_LIMIT:
                    return members
                cur = members[-1].as_user().identifier
            except OpenApiError as ex:
                # 若当前成员为频道最后一个元素时，API 会抛出代码为 130000 错误。
                if ex.code == 130000:
                    return members


    async def get_member(self, identifier: str):
        """
        异步获取当前频道的指定 ID 成员。

        参数：
            - identifier: 成员 ID

        返回：
            以 `Member` 类型表示的成员。
        """

        props = await self._session.get(
            f"/guilds/{self.identifier}/members/{identifier}"
        )
        return Member(props)

    async def get_channels(self):
        """
        异步获取当前频道的所有子频道。

        返回：
            以 `Channel` 类型表示子频道的 `list` 集合。
        """

        return [
            channel
            for channel in await self._get_channels_core()
            if isinstance(channel, Channel)
        ]

    async def get_channel_groups(self):
        """
        异步获取当前频道的所有子频道组。

        返回：
            以 `ChannelGroup` 类型表示子频道组的 `list` 集合。
        """

        return [
            channel
            for channel in await self._get_channels_core()
            if isinstance(channel, ChannelGroup)
        ]

    async def _get_channels_core(self):
        """
        异步获取当前频道的所有子频道及子频道组。

        返回：
            以 `Channel` 类型表示子频道及以 `ChannelGroup` 类型表示子频道组的 `list` 集合。
        """

        channels = await self._session.get(
            f"/guilds/{self.identifier}/channels"
        )
        return [channel_parse(self._session, props) for props in channels]
