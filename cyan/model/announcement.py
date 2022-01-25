from typing import TYPE_CHECKING, Any, Dict
from cyan.bot import Bot
from cyan.model import Model

if TYPE_CHECKING:
    from cyan.model.message.message import ChannelMessage
    from cyan.model.channel import TextChannel
    from cyan.model.guild import Guild


class Announcement(Model):
    """
    公告。
    """

    _props: Dict[str, Any]
    _bot: Bot

    def __init__(self, bot: Bot, props: Dict[str, Any]) -> None:
        """
        初始化 `Announcement` 实例。

        参数：
            - bot: 公告所属机器人
            - props: 属性
        """

        self._props = props
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["message_id"]

    async def get_guild(self) -> "Guild":
        """
        异步获取当前公告所属频道。

        返回：
            以 `Guild` 类型表示的公告所属频道。
        """

        return await self.bot.get_guild(self._props["guild_id"])

    async def get_channel(self) -> "TextChannel":
        """
        异步获取当前公告所属子频道。

        返回：
            以 `TextChannel` 类型表示的公告所属子频道。
        """

        from cyan.model.channel import TextChannel

        channel = await self.bot.get_channel(self._props["channel_id"])
        assert isinstance(channel, TextChannel)
        return channel

    async def get_message(self) -> "ChannelMessage":
        """
        异步获取当前公告的消息。

        返回：
            以 `ChannelMessage` 类型表示的公告消息。
        """

        channel = await self.get_channel()
        return await channel.get_message(self._props["message_id"])
