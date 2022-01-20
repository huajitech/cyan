from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from frozendict import frozendict
from typing import TYPE_CHECKING, Any, Callable, Iterable

from cyan.bot import Bot
from cyan.model import Model
from cyan.model.user import User


if TYPE_CHECKING:
    from cyan.model.message import Message
    from cyan.model.channel import TextChannel


@dataclass
class MessageElementParseResult:
    top: bool
    elements: list["MessageElement"]


class MessageElement:
    """
    消息元素。
    """

    @abstractmethod
    def apply(self, elements: dict[str, Any]) -> None:
        """
        应用消息元素至消息。
        """

        raise NotImplementedError

    def __add__(self, obj: Any):
        from cyan.model.message.elements.content import PlainText

        if isinstance(obj, MessageElement):
            return MessageContent([self, obj])
        if isinstance(obj, MessageContent):
            obj.insert(0, self)
            return obj
        return MessageContent([self, PlainText(str(obj))])


class ContentElement(MessageElement):
    @abstractmethod
    def to_content(self) -> str:
        raise NotImplementedError

    def apply(self, elements: dict[str, Any]):
        content = elements.get("content", "")
        content += self.to_content()
        elements["content"] = content


MessageElementParser = Callable[[Bot, dict[str, Any]], MessageElementParseResult | None]
_message_element_parsers = list[MessageElementParser]()


def message_element_parser():
    def _decorate(func: MessageElementParser):
        _message_element_parsers.append(func)

    return _decorate


class MessageContent(list[MessageElement]):
    def to_dict(self):
        elements = dict[str, Any]()
        for element in self:
            element.apply(elements)
        return elements

    @staticmethod
    def from_dict(bot: Bot, _dict: dict[str, Any]):
        elements = list[MessageElement]()
        for parser in _message_element_parsers:
            result = parser(bot, frozendict(_dict))
            if not result:
                continue
            if result.top:
                result.elements.extend(elements)
                elements = result.elements
            else:
                elements.extend(result.elements)
        return MessageContent(elements)

    def __add__(self, obj: Any):
        from cyan.model.message.elements.content import PlainText

        if isinstance(obj, MessageElement):
            return MessageContent(super().__add__([obj]))
        elif isinstance(obj, str):
            return MessageContent(super().__add__([PlainText(obj)]))
        else:
            return MessageContent(super().__add__(obj))


class Message(Model):
    _bot: Bot
    _props: dict[str, Any]
    _content: MessageContent

    def __init__(
        self,
        bot: Bot,
        props: dict[str, Any],
        content: MessageContent
    ):
        self._bot = bot
        self._props = props
        self._content = content

    @property
    def content(self):
        return MessageContent(self._content)

    @property
    def bot(self):
        return self._bot

    @property
    def identifier(self):
        return self._props["id"]

    @property
    def sender(self):
        return User(self.bot, self._props["author"])

    @property
    def time(self):
        return datetime.fromisoformat(self._props["timestamp"])

    async def get_channel(self) -> "TextChannel":
        return await self.bot.get_channel(self._props["channel_id"])  # type: ignore

    async def get_guild(self):
        return await self.bot.get_guild(self._props["guild_id"])

    async def get_sender_as_member(self):
        guild = await self.get_guild()
        return await guild.get_member(self.sender.identifier)

    async def reply(self, message: Iterable[MessageElement] | "Message"):
        channel = await self.get_channel()
        await channel.reply(self, message)

    @staticmethod
    def from_dict(bot: Bot, _dict: dict[str, Any]):
        content = MessageContent.from_dict(bot, _dict)
        return Message(bot, _dict, content)


from . import elements  # type: ignore
