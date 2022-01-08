from datetime import datetime
from typing import Any

from cyan.model.guild import Guild
from cyan.model.user import User


class Member:
    """
    成员。
    """

    _guild: Guild
    _props: dict[str, Any]

    def __init__(self, guild: Guild, props: dict[str, Any]):
        """
        初始化 `Member` 实例。

        参数：
            - props: 属性
        """

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

    async def get_roles(self):
        """
        异步获取当前成员的所有所属身份组。

        返回：
            以 `Role` 类型表示当前成员所属身份组的 `tuple` 集合。
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
