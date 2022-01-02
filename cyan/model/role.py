from enum import Enum


class DefaultRole(Enum):
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
