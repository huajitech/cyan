from datetime import timedelta, datetime
from typing import Any
from httpx import AsyncClient

from cyan.color import ARGB
from cyan.exception import InvalidTargetError, OpenApiError
from cyan.bot import Bot


# 参考 https://bot.q.qq.com/wiki/develop/pythonsdk/api/member/get_guild_members.html#queryparams。
_MEMBER_QUERY_LIMIT = 1000


class Guild:
    """
    频道。
    """

    _props: dict[str, Any]
    _bot: Bot

    def __init__(self, bot: Bot, props: dict[str, Any]):
        """
        初始化 `Guild` 实例。

        参数：
            - bot: 机器人
            - props: 属性
        """

        self._props = props
        self._bot = bot

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

        from cyan.model.member import Member

        cur = None
        members = list[Member]()
        while True:
            params: dict[str, Any] = {"limit": _MEMBER_QUERY_LIMIT}
            params.update(
                {"after": cur} if cur else {}
            )
            try:
                response = await self._bot.get(
                    f"/guilds/{self.identifier}/members",
                    params
                )
                content = response.json()
                members.extend([Member(self._bot, self, member) for member in content])
                if len(content) < _MEMBER_QUERY_LIMIT:
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

        from cyan.model.member import Member

        response = await self._bot.get(f"/guilds/{self.identifier}/members/{identifier}")
        member = response.json()
        return Member(self._bot, self, member)

    async def get_channels(self):
        """
        异步获取当前频道的所有子频道。

        返回：
            以 `Channel` 类型表示子频道的 `list` 集合。
        """

        from cyan.model.channel import Channel

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

        from cyan.model.channel import ChannelGroup

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

        from cyan.model.channel import parse as channel_parse

        response = await self._bot.get(f"/guilds/{self.identifier}/channels")
        channels = response.json()
        return [channel_parse(self._bot, channel) for channel in channels]

    async def get_roles(self):
        """
        异步获取当前频道的所有身份组。

        返回：
            以 `Role` 类型表示身份组的 `list` 集合。
        """

        from cyan.model.role import Role

        response = await self._bot.get(f"/guilds/{self.identifier}/roles")
        roles = response.json()["roles"]
        return [Role(self._bot, self, role) for role in roles]

    async def get_role(self, identifier: str):
        """
        异步获取当前频道的指定 ID 身份组。

        参数：
            - identifier: 身份组 ID

        返回：
            以 `Role` 类型表示的身份组。
        """

        roles = await self.get_roles()
        for role in roles:
            if role.identifier == identifier:
                return role
        raise InvalidTargetError("所指定 ID 的身份组不存在。")

    async def create_role(
        self,
        name: str | None = None,
        color: ARGB | None = None,
        shown: bool | None = None
    ):
        """
        异步在当前频道创建身份组。

        参数：
            - identifier: 身份组 ID

        返回：
            以 `Role` 类型表示的身份组。
        """

        from cyan.model.role import Role

        _filter = {
            "name": int(name is not None),
            "color": int(color is not None),
            "hoist": int(shown is not None)
        }
        info = {
            "name": name,
            "color": color.to_hex() if color else None,
            "hoist": int(bool(shown))
        }
        content = {"filter": _filter, "info": info}
        response = await self._bot.post(
            f"/guilds/{self.identifier}/roles",
            content=content
        )
        return Role(self._bot, self, response.json()["role"])

    async def mute(self, duration: timedelta):
        """
        异步禁言当前频道指定时长。

        参数：
            - duration: 禁言时长。
        """

        content = {"mute_seconds": str(duration.seconds)}
        await self._bot.patch(f"/guilds/{self.identifier}/mute", content=content)

    async def mute_until(self, time: datetime):
        """
        异步禁言当前频道至指定时间。

        参数：
            - time: 禁言终止时间。
        """

        content = {"mute_end_timestamp": str(int(time.timestamp()))}
        await self._bot.patch(f"/guilds/{self.identifier}/mute", content=content)

    async def unmute(self):
        """
        异步解除当前频道的禁言。
        """

        await self.mute(timedelta())
