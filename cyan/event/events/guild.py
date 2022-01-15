from typing import Any

from cyan.event import Event, EventType, Intent
from cyan.model.guild import Guild


class _GuildEvent(Event):
    async def _parse_data(self, data: Any):
        return Guild(self._bot, data)


class GuildCreatedEvent(_GuildEvent):
    """
    当频道被创建时触发。

    触发时回调的数据类型为 `Guild`。
    """

    @staticmethod
    def get_event_type():
        return EventType("GUILD_CREATE", Intent.GUILD)


class GuildUpdatedEvent(_GuildEvent):
    """
    当频道信息更新时触发。

    触发时回调的数据类型为 `Guild`。
    """

    @staticmethod
    def get_event_type():
        return EventType("GUILD_UPDATE", Intent.GUILD)


class GuildDeletedEvent(_GuildEvent):
    """
    当频道被删除时触发。

    触发时回调的数据类型为 `Guild`。
    """

    @staticmethod
    def get_event_type():
        return EventType("GUILD_DELETE", Intent.GUILD)
