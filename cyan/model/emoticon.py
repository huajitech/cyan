from typing import Any, Dict, NoReturn, Union

from cyan.exception import NotSupportedError
from cyan.model import Model


class Emoticon(Model):
    """
    表情。
    """

    _identifier: str

    def __init__(self, identifier: str) -> None:
        """
        初始化 `Emoticon` 实例。

        参数:
            - identifier: 表情 ID
        """

        self._identifier = identifier

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def bot(self) -> NoReturn:
        """
        注意:
            `Emoticon` 实例不储存 `Bot` 信息。
            尝试获取当前属性会抛出 `NotSupportedError`。
        """

        raise NotSupportedError


def parse(_dict: Dict[str, Any]) -> Union[str, Emoticon, None]:
    """
    解析表情信息字典为 `str` 或 `Emoticon` 类型。

    参数:
        _dict: 将用于解析的字典

    返回:
        当表情类型为系统表情时返回以 `Emoticon` 类型表示的系统表情；
        当表情类型为 Emoji 时返回以 `str` 类型表示的 Emoji；
        当表情类型未知时返回 `None`。
    """

    _type = _dict["type"]
    if _type == 1:
        return Emoticon(_dict["id"])
    elif _type == 2:
        return chr(int(_dict["id"]))
    else:
        return None
