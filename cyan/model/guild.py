from datetime import timedelta, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from httpx import AsyncClient

from cyan.color import ARGB
from cyan.exception import InvalidTargetError, OpenApiError
from cyan.bot import Bot
from cyan.model import Model
from cyan.model.renovatable import AsyncRenovatable
from cyan.model.announcement import Announcement


if TYPE_CHECKING:
    from cyan.model.message.message import ChannelMessage
    from cyan.model.channel import Channel, ChannelGroup
    from cyan.model.member import Member
    from cyan.model.role import Role


# 参考 https://bot.q.qq.com/wiki/develop/pythonsdk/api/member/get_guild_members.html#queryparams。
_MEMBER_QUERY_LIMIT = 1000


class Guild(Model, AsyncRenovatable["Guild"]):
    """
    频道。
    """

    _props: Dict[str, Any]
    _bot: Bot

    def __init__(self, bot: Bot, props: Dict[str, Any]) -> None:
        """
        初始化 `Guild` 实例。

        参数：
            - bot: 频道所属机器人
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

    async def get_icon(self) -> bytes:
        """
        异步获取频道头像。

        返回：
            以 `bytes` 类型表示的图像文件内容。
        """

        client = AsyncClient()
        response = await client.get(self._props["icon"])  # type: ignore
        return response.content

    async def get_members(self) -> List["Member"]:
        """
        异步获取当前频道的所有成员。

        返回：
            以 `Member` 类型表示成员的 `list` 集合。
        """

        from cyan.model.member import Member

        cur = None
        members: List[Member] = []
        while True:
            params: Dict[str, Any] = {"limit": _MEMBER_QUERY_LIMIT}
            if cur:
                params["after"] = cur
            try:
                response = await self.bot.get(
                    f"/guilds/{self.identifier}/members",
                    params
                )
                content = response.json()
                members.extend([Member(self.bot, self, member) for member in content])
                if len(content) < _MEMBER_QUERY_LIMIT:
                    return members
                cur = members[-1].identifier
            except OpenApiError as ex:
                # 若当前成员为频道最后一个元素时，API 会抛出代码为 130000 错误。
                if ex.code == 130000:
                    return members

    async def get_member(self, identifier: str) -> "Member":
        """
        异步获取当前频道的指定 ID 成员。

        参数：
            - identifier: 成员 ID

        返回：
            以 `Member` 类型表示的成员。
        """

        from cyan.model.member import Member

        response = await self.bot.get(f"/guilds/{self.identifier}/members/{identifier}")
        member = response.json()
        return Member(self.bot, self, member)

    async def get_channels(self) -> List["Channel"]:
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

    async def get_channel_groups(self) -> List["ChannelGroup"]:
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

    async def _get_channels_core(self) -> List[Union["Channel", "ChannelGroup"]]:
        from cyan.model.channel import parse as channel_parse

        response = await self.bot.get(f"/guilds/{self.identifier}/channels")
        channels = response.json()
        return [await channel_parse(self.bot, channel, self) for channel in channels]

    async def get_owner(self) -> Optional["Member"]:
        """
        异步获取频道所有者。

        返回：
            当存在频道所有者时，返回以 `Member` 类型表示的当前频道所有者；
            若不存在，则返回 `None`。
        """

        identifier = self._props["owner_id"]
        try:
            return await self.get_member(identifier)
        except OpenApiError as ex:
            if ex.code == 50001:
                return None
            raise

    async def get_roles(self) -> List["Role"]:
        """
        异步获取当前频道的所有身份组。

        返回：
            以 `Role` 类型表示身份组的 `list` 集合。
        """

        from cyan.model.role import Role

        response = await self.bot.get(f"/guilds/{self.identifier}/roles")
        roles = response.json()["roles"]
        return [Role(self.bot, self, role) for role in roles]

    async def get_role(self, identifier: str) -> "Role":
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
        name: Optional[str] = None,
        color: Optional[ARGB] = None,
        shown: Optional[bool] = None
    ) -> "Role":
        """
        异步在当前频道创建身份组。

        参数：
            - name: 身份组名称
            - color: 身份组颜色
            - shown: 身份组是否在成员列表中单独展示

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
        response = await self.bot.post(
            f"/guilds/{self.identifier}/roles",
            content=content
        )
        return Role(self.bot, self, response.json()["role"])

    async def mute(self, duration: timedelta) -> None:
        """
        异步禁言当前频道指定时长。

        参数：
            - duration: 禁言时长
        """

        content = {"mute_seconds": str(duration.seconds)}
        await self.bot.patch(f"/guilds/{self.identifier}/mute", content=content)

    async def mute_until(self, time: datetime) -> None:
        """
        异步禁言当前频道至指定时间。

        参数：
            - time: 禁言终止时间
        """

        content = {"mute_end_timestamp": str(int(time.timestamp()))}
        await self.bot.patch(f"/guilds/{self.identifier}/mute", content=content)

    async def unmute(self) -> None:
        """
        异步解除当前频道的禁言。
        """

        await self.mute(timedelta())

    async def get_administrators(self) -> List["Member"]:
        """
        异步获取当前频道的所有管理员。

        返回：
            以 `Member` 类型表示管理员的 `list` 集合。
        """

        from cyan.model.role import DefaultRoleId

        members = await self.get_members()
        return [
            member for member in members
            if DefaultRoleId.ADMINISTRATOR in [
                role.identifier for role in await member.get_roles()
            ]
        ]

    async def add_administrator(self, member: "Member") -> None:
        """
        异步添加管理员到当前频道。

        参数：
            - member: 将要作为频道管理员的成员
        """

        from cyan.model.role import DefaultRoleId

        await self.bot.put(
            f"/guilds/{self.identifier}/members/{member.identifier}"
            f"/roles/{DefaultRoleId.ADMINISTRATOR}"
        )

    async def remove_administrator(self, member: "Member") -> None:
        """
        异步从当前频道移除指定管理员。

        参数：
            - member: 将要从当前频道移除的管理员
        """

        from cyan.model.role import DefaultRoleId

        await self.bot.delete(
            f"/guilds/{self.identifier}/members/{member.identifier}"
            f"/roles/{DefaultRoleId.ADMINISTRATOR}"
        )

    async def remove(self, member: "Member") -> None:
        """
        异步从当前频道移除指定成员。

        参数：
            - member: 将要从当前频道移除的成员
        """

        await self.bot.delete(f"/guilds/{self.identifier}/members/{member.identifier}")

    async def remove_role(self, role: "Role") -> None:
        """
        异步从当前频道移除指定身份组。

        参数：
            - role: 将要从当前频道移除的身份组
        """

        await self.bot.delete(f"/guilds/{self.identifier}/roles/{role.identifier}")

    async def announce(self, message: "ChannelMessage") -> Announcement:
        """
        异步在当前频道公告指定消息。

        参数：
            - message: 将要在当前频道公告的消息

        返回：
            以 `Announcement` 类型表示的公告。
        """

        channel = await message.get_source()
        content = {"message_id": message.identifier, "channel_id": channel.identifier}
        response = await self.bot.post(f"/guilds/{self.identifier}/announces", content=content)
        announcement = response.json()
        return Announcement(self.bot, announcement)

    async def recall_announcement(self) -> None:
        """
        异步撤销当前频道的公告。
        """

        await self.bot.delete(f"/guilds/{self.identifier}/announces/all")

    async def renovate(self) -> "Guild":
        return await self.bot.get_guild(self.identifier)
