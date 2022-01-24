from typing import Any

from cyan.event import Event, EventInfo, Intent
from cyan.model.member import Member


class _MemberEvent(Event):
    async def _parse_data(self, data: dict[str, Any]) -> Member:
        guild_identifier = data["guild_id"]
        guild = await self._bot.get_guild(guild_identifier)
        return Member(self._bot, guild, data)


class MemberJoinedEvent(_MemberEvent):
    """
    当新成员加入频道时触发。

    触发时回调的数据类型为 `Member`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("GUILD_MEMBER_ADD", Intent.MEMBER)


class MemberUpdatedEvent(_MemberEvent):
    """
    当成员信息更新时触发。

    触发时回调的数据类型为 `Member`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("GUILD_MEMBER_UPDATE", Intent.MEMBER)


class MemberLeftEvent(_MemberEvent):
    """
    当成员离开频道时触发。

    触发时回调的数据类型为 `Member`。
    """

    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("GUILD_MEMBER_REMOVE", Intent.MEMBER)
