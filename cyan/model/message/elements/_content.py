import re
from re import Match, Pattern
from abc import abstractmethod
from typing import Any
from typing import Any, TypeVar

from cyan.bot import Bot
from cyan.model.channel import Channel
from cyan.model.message import (
    ContentElement,
    MessageElement,
    MessageElementParseResult,
    message_element_parser
)
from cyan.model.user import User


class ParsableContentElement(ContentElement):
    @staticmethod
    @abstractmethod
    def get_parse_regex() -> Pattern[str]:
        """
        获取解析 `Regex`。

        返回：
            以 `Pattern` 类型表示用于解析当前类型的 `Regex`。
        """

        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse(bot: Bot, _dict: dict[str, Any], match: Match[str]) -> ContentElement | None:
        """
        解析匹配结果。

        参数：
            - bot: 请求解析的机器人实例
            - _dict: API 返回字典
            - match: 匹配结果

        返回：
            当解析成功时，返回以 `ContentElement` 类型表示的元素；否则，返回 `None`。
        """

        raise NotImplementedError


_element_parsables = list[type[ParsableContentElement]]()


_T_ContentElement = TypeVar("_T_ContentElement", bound=ParsableContentElement)


def parsable_content_element(cls: type[_T_ContentElement]):
    """
    装饰 `ParsableContentElement` 以用于 `ContentElement` 消息元素解析。
    """

    _element_parsables.append(cls)
    return cls


@message_element_parser()
def parse_content(bot: Bot, _dict: dict[str, Any]):
    content: str = _dict["content"]
    if not content:
        return None
    matches = [
        (_type, match)
        for _type in _element_parsables
        for match in _type.get_parse_regex().finditer(content)
    ]
    matches.sort(key=lambda match: match[1].start())
    if not matches:
        return MessageElementParseResult(True, [PlainText(content)])
    begin = content[:matches[0][1].start()]
    end = content[matches[-1][1].end():]
    result = list[MessageElement]()
    if begin:
        result.append(PlainText(begin))
    last_match = None
    for match in matches:
        if last_match:
            plain_text_content = content[last_match.end():match[1].start()]
            if plain_text_content:
                result.append(PlainText(plain_text_content))
        element = match[0].parse(bot, _dict, match[1])
        if element:
            result.append(element)
        last_match = match[1]
    if end:
        result.append(PlainText(end))
    return MessageElementParseResult(True, result)


class PlainText(ContentElement):
    """
    纯文本。
    """

    _content: str

    def __init__(self, content: str):
        """
        初始化 `PlainText` 实例。

        参数：
            - content: 内容
        """

        self._content = content

    @property
    def content(self):
        """
        纯文本内容。
        """

        return self._content

    def to_content(self) -> str:
        return self.content

    def __str__(self):
        return self.content

    def __eq__(self, obj: Any):
        if isinstance(obj, PlainText):
            return obj._content == self.content
        if isinstance(obj, str):
            return obj == self.content
        return False


@parsable_content_element
class Mention(ParsableContentElement):
    """
    提及。
    """

    _target: User

    def __init__(self, target: User):
        """
        初始化 `Mention` 实例。

        参数：
            - target: 目标用户
        """

        self._target = target

    @property
    def target(self):
        """
        提及目标。
        """

        return self._target

    @staticmethod
    def get_parse_regex():
        return re.compile(r"<@!{0,1}([\d\w]+)>")

    @staticmethod
    def parse(bot: Bot, _dict: dict[str, Any], match: Match[str]):
        mentions = _dict.get("mentions", None)
        if mentions:
            for mention in mentions:
                user = User(bot, mention)
                if mention["id"] == match.group(1):
                    return Mention(user)
        return None

    def to_content(self):
        return f"<@{self.target.identifier}>"

    def __str__(self):
        return f"@{self.target.name}"


@parsable_content_element
class MentionAll(ParsableContentElement):
    """
    提及全体成员。
    """

    def __init__(self):
        """
        初始化 `MentionAll` 实例。
        """

        pass

    @staticmethod
    def get_parse_regex():
        return re.compile(r"@everyone")

    @staticmethod
    def parse(bot: Bot, _dict: dict[str, Any], match: Match[str]):
        return MentionAll()

    def to_content(self):
        return "@everyone"

    def __str__(self):
        return "@全体成员"


class ChannelLink(ContentElement):
    """
    子频道链接。
    """

    _target: Channel

    def __init__(self, target: Channel):
        """
        初始化 `ChannelLink` 实例。

        - target: 目标子频道
        """

        self._target = target

    @property
    def target(self):
        """
        目标子频道。
        """

        return self._target

    def to_content(self):
        return f"<#{self.target.identifier}>"

    def __str__(self):
        return f"#{self.target.name}"
