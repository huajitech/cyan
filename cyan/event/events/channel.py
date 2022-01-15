from typing import Any

from cyan.event import Event, EventType, Intent
from cyan.model.channel import Channel


class ChannelCreatedEvent(Event):
    """
    当子频道被创建时触发。
    """

    @staticmethod
    def get_event_type():
        return EventType("CHANNEL_CREATE", Intent.GUILD)

    def _parse_data(self, data: Any):
        return Channel(self._bot, data)


class ChannelUpdatedEvent(Event):
    """
    当子频道信息更新时触发。
    """

    @staticmethod
    def get_event_type():
        return EventType("CHANNEL_UPDATE", Intent.GUILD)

    def _parse_data(self, data: Any):
        return Channel(self._bot, data)


class ChannelDeletedEvent(Event):
    """
    当子频道被删除时触发。
    """

    @staticmethod
    def get_event_type():
        return EventType("CHANNEL_DELETE", Intent.GUILD)

    def _parse_data(self, data: Any):
        return Channel(self._bot, data)
