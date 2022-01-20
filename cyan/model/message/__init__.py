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
    """
    消息元素解析结果。
    """

    top: bool
    """
    元素是否置顶。
    """

    elements: list["MessageElement"]
    """
    解析结果所有元素的 `list` 类型集合。
    """


class MessageElement:
    """
    消息元素。
    """

    @abstractmethod
    def apply(self, _dict: dict[str, Any]) -> None:
        """
        应用消息元素至消息。

        参数：
            - _dict: 将用于发送至 API 的字典。
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
        """
        转换为可被 API 解析的字符串内容。

        返回：
            可被 API 解析的当前实例的等效字符串内容。
        """

        raise NotImplementedError

    def apply(self, _dict: dict[str, Any]):
        content = _dict.get("content", "")
        content += self.to_content()
        _dict["content"] = content


MessageElementParser = Callable[[Bot, dict[str, Any]], MessageElementParseResult | None]
"""
消息元素解析器。

参数：
    - `Bot`: 请求解析的机器人实例
    - `dict[str, Any]`: API 返回字典

返回：
    当解析成功时，返回以 `MessageElementParseResult` 类型表示的解析结果；否则，返回 `None`。
"""

_message_element_parsers = list[MessageElementParser]()


def message_element_parser():
    """
    装饰消息元素解析器以用于消息元素解析。
    """

    def _decorate(func: MessageElementParser):
        _message_element_parsers.append(func)

    return _decorate


class MessageContent(list[MessageElement]):
    """
    消息内容。
    """

    def to_dict(self):
        """
        转换为可被 API 解析的字典。

        返回：
            可被 API 解析的当前实例的等效字典。
        """

        elements = dict[str, Any]()
        for element in self:
            element.apply(elements)
        return elements

    @staticmethod
    def from_dict(bot: Bot, _dict: dict[str, Any]):
        """
        解析消息内容字典为 `MessageContent` 实例。

        参数：
            - bot: 请求解析的机器人实例
            - _dict: 将用于解析的消息内容字典

        返回：
            以 `MessageContent` 类型表示的消息内容。
        """

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
    def bot(self):
        return self._bot

    @property
    def identifier(self):
        return self._props["id"]

    @property
    def content(self):
        """
        消息内容。
        """

        return MessageContent(self._content)

    @property
    def sender(self):
        """
        消息发送者。
        """

        return User(self.bot, self._props["author"])

    @property
    def time(self):
        """
        消息发送时间。
        """

        return datetime.fromisoformat(self._props["timestamp"])

    async def get_channel(self) -> "TextChannel":
        """
        异步获取消息的附属子频道。

        返回：
            以 `Member` 类型表示的消息附属子频道。
        """

        return await self.bot.get_channel(self._props["channel_id"])  # type: ignore

    async def get_guild(self):
        """
        异步获取消息的附属频道。

        返回：
            以 `Guild` 类型表示的消息附属频道。
        """

        return await self.bot.get_guild(self._props["guild_id"])

    async def get_sender_as_member(self):
        """
        异步获取消息发送者的 `Member` 实例。

        返回：
            以 `Member` 类型表示的消息发送者。
        """

        guild = await self.get_guild()
        return await guild.get_member(self.sender.identifier)

    async def reply(self, message: Iterable[MessageElement] | "Message"):
        """
        异步回复当前消息。

        参数：
            - message: 回应消息
        """

        channel = await self.get_channel()
        await channel.reply(self, message)

    @staticmethod
    def from_dict(bot: Bot, _dict: dict[str, Any]):
        """
        解析消息内容字典为 `Message` 实例。

        参数：
            - bot: 请求解析的机器人实例
            - _dict: 将用于解析的消息内容字典

        返回：
            以 `Message` 类型表示的消息。
        """

        content = MessageContent.from_dict(bot, _dict)
        return Message(bot, _dict, content)


from . import elements  # type: ignore
