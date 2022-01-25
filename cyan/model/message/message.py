from typing import TYPE_CHECKING, Any, Dict

from cyan.bot import Bot
from cyan.model.message import Message
from cyan.model._dms import DirectMessageSubject

if TYPE_CHECKING:
    from cyan.model.member import Member
    from cyan.model.channel import TextChannel
    from cyan.model.user import ChattableUser


class ChannelMessage(Message["ChannelMessage"]):
    """
    子频道消息。
    """

    async def get_source(self) -> "TextChannel":
        """
        异步获取消息来源。

        返回：
            以 `TextChannel` 类型表示的源文字频道。
        """

        from cyan.model.channel import TextChannel

        channel = await self.bot.get_channel(self._props["channel_id"])
        assert isinstance(channel, TextChannel)
        return channel

    async def get_sender_as_member(self) -> "Member":
        """
        异步获取消息发送者的 `Member` 实例。

        返回：
            以 `Member` 类型表示的消息发送者。
        """

        channel = await self.get_source()
        return await channel.guild.get_member(self.sender.identifier)

    @staticmethod
    def parse(bot: Bot, _dict: Dict[str, Any]) -> "ChannelMessage":
        content = Message._get_content(bot, _dict)
        return ChannelMessage(bot, _dict, content)


class UserMessage(Message["UserMessage"]):
    """
    用户消息。
    """

    async def get_source(self) -> "ChattableUser":
        """
        异步获取消息来源。

        返回：
            以 `ChattableUser` 类型表示的源用户。
        """

        from cyan.model.user import ChattableUser

        dms = DirectMessageSubject(self._props["guild_id"], self._props["channel_id"])
        return ChattableUser(self.sender, dms)

    @staticmethod
    def parse(bot: Bot, _dict: Dict[str, Any]) -> "UserMessage":
        content = Message._get_content(bot, _dict)
        return UserMessage(bot, _dict, content)
