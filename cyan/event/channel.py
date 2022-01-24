from typing import Any

from cyan.event import Event, EventInfo, Intent, NotSupported
from cyan.model.channel import Channel, parse


class _ChannelEvent(Event):
    async def _parse_data(self, data: Any) -> Channel:
        channel = await parse(self._bot, data)
        if not isinstance(channel, Channel):
            raise NotSupported
        return channel


class ChannelCreatedEvent(_ChannelEvent):
    """
    当子频道被创建时触发。

    触发时回调的数据类型为 `Channel`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("CHANNEL_CREATE", Intent.GUILD)


class ChannelUpdatedEvent(_ChannelEvent):
    """
    当子频道信息更新时触发。

    触发时回调的数据类型为 `Channel`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("CHANNEL_UPDATE", Intent.GUILD)


class ChannelDeletedEvent(_ChannelEvent):
    """
    当子频道被删除时触发。

    触发时回调的数据类型为 `Channel`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("CHANNEL_DELETE", Intent.GUILD)
