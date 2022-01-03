from enum import EnumMeta
from typing import Any


def get_enum_key(
    enum: EnumMeta,
    value: Any,
    default: Any = ...
) -> Any:
    return enum._value2member_map_.get(
        value,
        value if default == ... else default
    )
