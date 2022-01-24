from typing import Any

from cyan.event import Event, EventInfo, Intent
from cyan.model.message import Message, MessageAuditInfo


class ChannelMessageReceivedEvent(Event):
    """
    当接收到子频道用户所发送含提及机器人消息时触发。

    触发时回调的数据类型为 `Message`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("AT_MESSAGE_CREATE", Intent.MENTION)

    async def _parse_data(self, data: dict[str, Any]) -> Message:
        return Message.from_dict(self._bot, data)


class MessageAuditPassedEventData:
    """
    `MessageAuditPassedEvent` 事件数据。
    """

    _audit_info: MessageAuditInfo
    _message: Message

    def __init__(self, audit_info: MessageAuditInfo, message: Message) -> None:
        """
        初始化 `MessageAuditPassedEventData` 实例。

        参数：
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
    def message(self) -> Message:
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

    async def _parse_data(self, data: Any) -> MessageAuditPassedEventData:
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

    async def _parse_data(self, data: Any) -> MessageAuditInfo:
        return MessageAuditInfo(self._bot, data)
