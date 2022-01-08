from enum import Enum
from typing import Any

from cyan.color import ARGB


class DefaultRoleId(Enum):
    """
    默认身份组 ID。
    """

    DEFAULT = "1"
    """
    默认。
    """

    ADMINISTRATOR = "2"
    """
    管理员。
    """

    OWNER = "4"
    """
    创建者。
    """

    OPERATOR = "5"
    """
    子频道管理员。
    """


class Role:
    """
    身份组。
    """

    def __init__(self, props: dict[str, Any]):
        """
        初始化 `Role` 实例。

        参数：
            - props: 属性
        """

        self._props = props

    @property
    def identifier(self) -> str:
        """
        身份组 ID。
        """

        return self._props["id"]

    @property
    def name(self) -> str:
        """
        身份组名称。
        """

        return self._props["name"]

    @property
    def capacity(self) -> int:
        """
        身份组容量。
        """

        return self._props["member_limit"]

    @property
    def color(self):
        """
        身份组颜色。
        """

        return ARGB.from_hex(self._props["color"])

    @property
    def shown(self) -> bool:
        """
        身份组是否在成员列表中单独展示。
        """

        return bool(self._props["hoist"])
