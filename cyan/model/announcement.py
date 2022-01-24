from typing import TYPE_CHECKING, Any
from cyan.bot import Bot
from cyan.exception import OperationFailedError
from cyan.model import Model

if TYPE_CHECKING:
    from cyan.model.message import Message
    from cyan.model.channel import TextChannel
    from cyan.model.guild import Guild


class Announcement(Model):
    """
    公告。
    """

    _props: dict[str, Any]
    _bot: Bot

    def __init__(self, bot: Bot, props: dict[str, Any]) -> None:
        """
        初始化 `Announcement` 实例。

        参数：
            - bot: 机器人
            - props: 属性
        """

        self._props = props
        self._bot = bot
        print(props)

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["message_id"]

    async def get_guild(self) -> "Guild":
        """
        异步获取当前公告所属频道。
        """

        return await self.bot.get_guild(self._props["guild_id"])

    async def get_channel(self) -> "TextChannel":
        """
        异步获取当前公告所属子频道。
        """

        from cyan.model.channel import TextChannel

        channel = await self.bot.get_channel(self._props["channel_id"])
        if not isinstance(channel, TextChannel):
            raise OperationFailedError("当前公告所属子频道不为文字子频道。")
        return channel
        
    async def get_message(self) -> "Message":
        """
        异步获取当前公告的消息。
        """

        channel = await self.get_channel()
        return await channel.get_message(self._props["message_id"])
