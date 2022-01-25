from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from frozendict import frozendict
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, Generic,
    Iterable, TypeVar, Union, List, Optional
)

from cyan.bot import Bot
from cyan.model.guild import Guild
from cyan.model import ChattableModel, Model


if TYPE_CHECKING:
    from cyan.model.user import User
    from cyan.model.channel import TextChannel


_T_Message = TypeVar("_T_Message", bound="Message")


class MessageElement:
    """
    消息元素。
    """

    @abstractmethod
    def apply(self, _dict: Dict[str, Any]) -> None:
        """
        应用消息元素至消息。

        参数：
            - _dict: 将用于发送至 API 的字典。
        """

        raise NotImplementedError


@dataclass
class MessageElementParseResult:
    """
    消息元素解析结果。
    """

    top: bool
    """
    元素是否置顶。
    """

    elements: List[MessageElement]
    """
    解析结果所有元素的 `list` 类型集合。
    """


class ContentElement(MessageElement):
    @abstractmethod
    def to_content(self) -> str:
        """
        转换为可被 API 解析的字符串内容。

        返回：
            可被 API 解析的当前实例的等效字符串内容。
        """

        raise NotImplementedError

    def apply(self, _dict: Dict[str, Any]) -> None:
        content = _dict.get("content", "")
        content += self.to_content()
        _dict["content"] = content


MessageElementParser = Callable[[Bot, Dict[str, Any]], Optional[MessageElementParseResult]]
"""
消息元素解析器。

参数：
    - `Bot`: 请求解析的机器人实例
    - `Dict[str, Any]`: API 返回字典

返回：
    当解析成功时，返回以 `MessageElementParseResult` 类型表示的解析结果；否则，返回 `None`。
"""

_message_element_parsers: List[MessageElementParser] = []


def message_element_parser() -> Callable[[MessageElementParser], None]:
    """
    装饰消息元素解析器以用于消息元素解析。
    """

    def _decorate(func: MessageElementParser):
        _message_element_parsers.append(func)

    return _decorate


class MessageContent(List[MessageElement]):
    """
    消息内容。
    """

    def extract_plain_text(self) -> str:
        """
        提取纯文本。

        返回：
            以 `str` 类型表示消息内容的所有纯文本。
        """

        from cyan.model.message.content import PlainText

        return " ".join([element.content for element in self if isinstance(element, PlainText)])

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为可被 API 解析的字典。

        返回：
            可被 API 解析的当前实例的等效字典。
        """

        elements: Dict[str, Any] = {}
        for element in self:
            element.apply(elements)
        return elements

    def __str__(self) -> str:
        return "".join(map(str, self))


class MessageAuditInfo(Model):
    """
    消息审核信息。
    """

    _bot: Bot
    _props: Dict[str, Any]

    def __init__(self, bot: Bot, props: Dict[str, Any]) -> None:
        """
        初始化 `MessageAuditInfo` 实例。

        参数：
            - bot: 消息审核信息所属机器人
            - props: 属性
        """

        self._bot = bot
        self._props = props

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["data"]["message_audit"]["audit_id"]

    async def get_guild(self) -> "Guild":
        """
        异步获取当前消息审核信息所属频道。
        """

        return await self.bot.get_guild(self._props["guild_id"])

    async def get_channel(self) -> "TextChannel":
        """
        异步获取当前消息审核信息所属子频道。
        """

        from cyan.model.channel import TextChannel

        channel = await self.bot.get_channel(self._props["channel_id"])
        assert isinstance(channel, TextChannel)
        return channel


class Message(Model, Generic[_T_Message]):
    """
    消息。
    """

    _bot: Bot
    _props: Dict[str, Any]
    _content: MessageContent

    def __init__(
        self,
        bot: Bot,
        props: Dict[str, Any],
        content: MessageContent
    ) -> None:
        """
        初始化 `Message` 实例。

        参数：
            - bot: 消息所属机器人
            - props: 属性
            - content: 消息内容
        """

        self._bot = bot
        self._props = props
        self._content = content

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["id"]

    @property
    @abstractmethod
    def sender(self) -> "User":
        """
        消息发送者。
        """

        from cyan.model.user import User

        return User(self.bot, self._props["author"])

    @property
    def time(self) -> datetime:
        """
        消息发送时间。
        """

        return datetime.fromisoformat(self._props["timestamp"])

    @property
    def content(self) -> MessageContent:
        """
        消息内容。
        """

        return MessageContent(self._content)

    @abstractmethod
    async def get_source(self) -> ChattableModel[_T_Message]:
        """
        异步获取消息来源。

        返回：
            以 `ChattableModel[T]` 为基类的 `Model` 消息源。
        """

        raise NotImplementedError

    async def reply(self: _T_Message, *message: "Sendable") -> _T_Message:
        """
        异步回复当前消息。

        参数：
            - message: 回应消息

        返回：
            当消息需被审核时返回以 `MessageAuditInfo` 类型表示的消息审核信息；
            否则，返回表示以 `Message` 类型表示的所发送消息。
        """

        source = await self.get_source()
        return await source.reply(self, *message)

    @staticmethod
    def parse(bot: Bot, _dict: Dict[str, Any]) -> _T_Message:
        """
        解析消息内容字典为 `Message` 实例。

        参数：
            - bot: 请求解析的机器人实例
            - _dict: 将用于解析的消息内容字典

        返回：
            以 `Message` 类型表示的消息。
        """

        raise NotImplementedError

    @staticmethod
    def _get_content(bot: Bot, _dict: Dict[str, Any]) -> MessageContent:
        elements = MessageContent()
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


Sendable = Union[MessageElement, str, Message[Any], Iterable[MessageElement]]


def create_message_content(*elements: Sendable) -> MessageContent:
    """
    创建 `MessageContent` 实例。

    指定元素类型若为 `MessageElement` 则直接呈现；
    若为 `str` 则转换为 `PlainText` 类型呈现；
    若为 `Iterable[MessageElement]` 则取出其中元素呈现；
    若为 `ChannelMessage` 则获取其中内容并取出其中元素呈现。

    参数：
        - elements: 元素

    返回：
        包含指定元素的 `MessageContent`。
    """

    from cyan.model.message.content import PlainText

    content = MessageContent()
    for element in elements:
        if isinstance(element, MessageElement):
            content.append(element)
        elif isinstance(element, str):
            content.append(PlainText(element))
        elif isinstance(element, Message):
            content.extend(element.content)
        else:
            content.extend(element)
    return content


from .content import *
