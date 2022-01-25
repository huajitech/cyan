from enum import EnumMeta
from typing import Any


def get_enum_key(enum: EnumMeta, value: Any, default: Any = ...) -> Any:
    """
    获取 `Enum` 值对应的键。

    参数：
        - enum: Enum 类型
        - value: 将要查询对应键的值
        - default: 当对应键不存在时返回的默认值（默认返回传入的 `value` 参数）
    """

    return enum._value2member_map_.get(
        value,
        value if default == ... else default
    )
