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
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse(bot: Bot, _dict: dict[str, Any], match: Match[str]) -> ContentElement | None:
        raise NotImplementedError


_element_parsables = list[type[ParsableContentElement]]()


_T_ContentElement = TypeVar("_T_ContentElement", bound=ParsableContentElement)


def parsable_content_element(cls: type[_T_ContentElement]):
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
    _content: str

    def __init__(self, content: str):
        self._content = content

    def to_content(self) -> str:
        return self._content

    def __str__(self):
        return self._content

    def __eq__(self, obj: Any):
        if isinstance(obj, PlainText):
            return obj._content == self._content
        if isinstance(obj, str):
            return obj == self._content
        return False


@parsable_content_element
class Mention(ParsableContentElement):
    _target: User

    def __init__(self, target: User):
        self._target = target

    @property
    def target(self):
        return self._target

    @staticmethod
    def get_parse_regex():
        return re.compile(r"<@!([\d\w]+)>")

    @staticmethod
    def parse(bot: Bot, _dict: dict[str, Any], match: Match[str]):
        mentions = _dict["mentions"]
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
    _target: User

    def __init__(self):
        pass

    @property
    def target(self):
        return self._target

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
    _target: Channel

    def __init__(self, target: Channel):
        self._target = target

    @property
    def target(self):
        return self._target

    def to_content(self):
        return f"<#{self.target.identifier}>"

    def __str__(self):
        return f"#{self.target.name}"
