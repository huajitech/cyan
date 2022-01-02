from datetime import datetime
from typing import Any

from cyan.model.user import User


class Member:
    """
    成员。
    """

    _props: dict[str, Any]

    def __init__(self, props: dict[str, Any]):
        """
        初始化 `Member` 实例。

        参数：
            - props: 属性
        """

        self._props = props

    @property
    def nickname(self) -> str:
        """
        用户昵称。
        """

        return self._props["nick"]

    @property
    def joined_time(self) -> datetime:
        """
        入群时间。
        """

        return self._props["joined_at"]

    @property
    def roles(self) -> tuple[str]:
        """
        成员角色。
        """

        return tuple[str](self._props["roles"])

    def as_user(self) -> User:
        """
        转换成员为用户。

        返回：
            当前实例的 `User` 形式。
        """

        return User(self._props["user"])
