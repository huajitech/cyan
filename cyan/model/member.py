from datetime import datetime, timedelta
from typing import Any

from cyan.bot import Bot
from cyan.model.guild import Guild
from cyan.model.user import User


class Member:
    """
    成员。
    """

    _bot: Bot
    _guild: Guild
    _props: dict[str, Any]

    def __init__(self, bot: Bot, guild: Guild, props: dict[str, Any]):
        """
        初始化 `Member` 实例。

        参数：
            - props: 属性
        """

        self._bot = bot
        self._guild = guild
        self._props = props

    @property
    def nickname(self) -> str:
        """
        成员昵称。
        """

        return self._props["nick"]

    @property
    def joined_time(self) -> datetime:
        """
        成员加入时间。
        """

        return self._props["joined_at"]

    @property
    def guild(self):
        """
        成员所属频道。
        """

        return self._guild

    async def get_roles(self):
        """
        异步获取当前成员的所有所属身份组。

        返回：
            以 `Role` 类型表示当前成员所属身份组的 `list` 集合。
        """

        roles = await self._guild.get_roles()
        role_map = dict([(role.identifier, role) for role in roles])
        return [role_map[role] for role in self._props["roles"]]

    def as_user(self) -> User:
        """
        转换成员为用户。

        返回：
            当前实例的 `User` 形式。
        """

        return User(self._props["user"])

    async def mute(self, duration: timedelta):
        """
        异步禁言当前成员指定时长。
        """

        content = {"mute_seconds": str(duration.seconds)}
        await self._bot.patch(
            f"/guilds/{self.guild.identifier}/members/{self.as_user().identifier}/mute",
            content=content
        )

    async def mute_until(self, time: datetime):
        """
        异步禁言当前成员至指定时间。
        """

        content = {"mute_end_timestamp": str(time.timestamp())}
        await self._bot.patch(
            f"/guilds/{self.guild.identifier}/members/{self.as_user().identifier}/mute",
            content=content
        )

    async def unmute(self):
        """
        异步解除当前频道的禁言。
        """

        await self.mute(timedelta())
