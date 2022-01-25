from datetime import datetime, timedelta
from typing import Any, Dict, List

from cyan.bot import Bot
from cyan.model import ChattableModel
from cyan.model.guild import Guild
from cyan.model.message import Sendable
from cyan.model.message.message import UserMessage
from cyan.model.renovatable import AsyncRenovatable
from cyan.model.role import Role
from cyan.model.user import ChattableUser, User
from cyan.model._dms import DirectMessageSubject


class Member(User, AsyncRenovatable["Member"], ChattableModel[UserMessage]):
    """
    成员。
    """

    _bot: Bot
    _guild: Guild
    _props: Dict[str, Any]
    _user: User

    def __init__(self, bot: Bot, guild: Guild, props: Dict[str, Any]) -> None:
        """
        初始化 `Member` 实例。

        参数：
            - bot: 成员所属机器人
            - guild: 成员所属频道
            - props: 属性
        """

        self._bot = bot
        self._guild = guild
        self._props = props
        self._user = User(bot, props["user"])

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._user.identifier

    @property
    def name(self) -> str:
        return self._user.name

    @property
    def is_bot(self) -> bool:
        return self._user.is_bot

    async def get_avatar(self) -> bytes:
        return await self._user.get_avatar()

    @property
    def alias(self) -> str:
        """
        成员别称。
        """

        return self._props["nick"]

    @property
    def joined_time(self) -> datetime:
        """
        成员加入时间。
        """

        return datetime.fromisoformat(self._props["joined_at"])

    @property
    def guild(self) -> Guild:
        """
        成员所属频道。
        """

        return self._guild

    async def get_roles(self) -> List[Role]:
        """
        异步获取当前成员的所有所属身份组。

        返回：
            以 `Role` 类型表示当前成员所属身份组的 `list` 集合。
        """

        roles = await self.guild.get_roles()
        role_map = dict([(role.identifier, role) for role in roles])
        return [role_map[role] for role in self._props["roles"]]

    async def mute(self, duration: timedelta) -> None:
        """
        异步禁言当前成员指定时长。
        """

        content = {"mute_seconds": str(duration.seconds)}
        await self.bot.patch(
            f"/guilds/{self.guild.identifier}/members/{self.identifier}/mute",
            content=content
        )

    async def mute_until(self, time: datetime) -> None:
        """
        异步禁言当前成员至指定时间。
        """

        content = {"mute_end_timestamp": str(time.timestamp())}
        await self.bot.patch(
            f"/guilds/{self.guild.identifier}/members/{self.identifier}/mute",
            content=content
        )

    async def unmute(self) -> None:
        """
        异步解除当前成员的禁言。
        """

        await self.mute(timedelta())

    async def send(self, *message: Sendable) -> UserMessage:
        user = await self._get_chattable_user()
        return await user.send(*message)

    async def reply(self, target: UserMessage, *message: "Sendable") -> UserMessage:
        user = await self._get_chattable_user()
        return await user.reply(target, *message)

    async def get_message(self, identifier: str) -> UserMessage:
        user = await self._get_chattable_user()
        return await user.get_message(identifier)

    async def _get_chattable_user(self) -> ChattableUser:
        content = {"recipient_id": self.identifier, "source_guild_id": self.guild.identifier}
        response = await self.bot.post("/users/@me/dms", content=content)
        data = response.json()
        dms = DirectMessageSubject(data["guild_id"], data["channel_id"])
        return ChattableUser(self._user, dms)

    async def renovate(self) -> "Member":
        guild = await self.guild.renovate()
        return await guild.get_member(self.identifier)
