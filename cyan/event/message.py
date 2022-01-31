from typing import Any, Dict, Union

from cyan.event import Event, EventInfo, Intent
from cyan.model.channel import Channel
from cyan.model.emoticon import Emoticon
from cyan.model.emoticon import parse as emoticon_parse
from cyan.model.member import Member
from cyan.model.message import MessageAuditInfo
from cyan.model.message.message import ChannelMessage, UserMessage


class ChannelMessageReceivedEvent(Event):
    """
    当接收到子频道用户所发送含提及机器人消息时触发。

    触发时回调的数据类型为 `ChannelMessage`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("AT_MESSAGE_CREATE", Intent.MENTION)

    async def _parse_data(self, data: Dict[str, Any]) -> ChannelMessage:
        return ChannelMessage.parse(self._bot, data)


class UserMessageReceivedEvent(Event):
    """
    当接收到用户与机器人私聊时触发。

    触发时回调的数据类型为 `UserMessage`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("DIRECT_MESSAGE_CREATE", Intent.DIRECT_MESSAGE)

    async def _parse_data(self, data: Dict[str, Any]) -> UserMessage:
        return UserMessage.parse(self._bot, data)


class MessageAuditPassedEventData:
    """
    `MessageAuditPassedEvent` 事件数据。
    """

    _audit_info: MessageAuditInfo
    _message: ChannelMessage

    def __init__(self, audit_info: MessageAuditInfo, message: ChannelMessage) -> None:
        """
        初始化 `MessageAuditPassedEventData` 实例。

        参数:
            - audit_info: 消息审核信息。
        """

        self._audit_info = audit_info
        self._message = message

    @property
    def audit_info(self) -> MessageAuditInfo:
        """
        消息审核信息。
        """

        return self._audit_info

    @property
    def message(self) -> ChannelMessage:
        """
        消息。
        """

        return self._message


class MessageAuditPassedEvent(Event):
    """
    当消息审核通过时触发。

    触发时回调的数据类型为 `MessageAuditPassedEventData`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("MESSAGE_AUDIT_PASS", Intent.MESSAGE_AUDIT)

    async def _parse_data(self, data: Dict[str, Any]) -> MessageAuditPassedEventData:
        audit_info = MessageAuditInfo(self._bot, data)
        channel = await audit_info.get_channel()
        message = await channel.get_message(data["message_id"])
        return MessageAuditPassedEventData(audit_info, message)


class MessageAuditRejectedEvent(Event):
    """
    当消息审核不通过时触发。

    触发时回调的数据类型为 `MessageAuditInfo`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("MESSAGE_AUDIT_REJECT", Intent.MESSAGE_AUDIT)

    async def _parse_data(self, data: Dict[str, Any]) -> MessageAuditInfo:
        return MessageAuditInfo(self._bot, data)


class UserExpressionEventData:
    """
    用户表态事件数据。
    """

    _channel: Channel
    _sender: Member
    _emoticon: Union[Emoticon, str, None]

    def __init__(
        self,
        channel: Channel,
        sender: Member,
        emoticon: Union[Emoticon, str, None]
    ) -> None:
        """
        初始化 `UserExpressionEventData` 实例。
        """

        self._channel = channel
        self._sender = sender
        self._emoticon = emoticon

    @property
    def channel(self) -> Channel:
        """
        频道。
        """

        return self._channel

    @property
    def sender(self) -> Member:
        """
        发送者。
        """

        return self._sender

    @property
    def emoticon(self) -> Union[Emoticon, str, None]:
        """
        表情。
        """

        return self._emoticon


class _UserExpressionEvent(Event):
    async def _parse_data(self, data: Dict[str, Any]) -> UserExpressionEventData:
        channel = await self._bot.get_channel(data["channel_id"])
        emoticon = emoticon_parse(data["emoji"])
        sender = await channel.guild.get_member(data["user_id"])
        return UserExpressionEventData(channel, sender, emoticon)


class UserExpressionReceivedEvent(_UserExpressionEvent):
    """
    当接收到用户发送表情表态时触发。

    触发时回调的数据类型为 `UserExpressionEventData`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("MESSAGE_REACTION_ADD", Intent.EXPRESSION)


class UserExpressionRecalledEvent(_UserExpressionEvent):
    """
    当用户撤回表情表态时触发。

    触发时回调的数据类型为 `UserExpressionEventData`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("MESSAGE_REACTION_REMOVE", Intent.EXPRESSION)
