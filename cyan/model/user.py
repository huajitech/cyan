from typing import Any, Dict, Optional
from httpx import AsyncClient

from cyan.bot import Bot
from cyan.model import ChattableModel, Model
from cyan.model._dms import DirectMessageSubject
from cyan.model.message import MessageContent, Sendable
from cyan.model.message.message import UserMessage


class User(Model):
    """
    用户。
    """

    _props: Dict[str, Any]
    _bot: Bot

    def __init__(self, bot: Bot, props: Dict[str, Any]) -> None:
        """
        初始化 `User` 实例。

        参数：
            - bot: 用户所属机器人
            - props: 属性
        """

        self._props = props
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["id"]

    @property
    def name(self) -> str:
        """
        用户名称。
        """

        return self._props["username"]

    @property
    def is_bot(self) -> bool:
        """
        用户是否为机器人。
        """

        return self._props["bot"]

    async def get_avatar(self) -> bytes:
        """
        异步获取用户头像。

        返回：
            以 `bytes` 类型表示的图像文件内容。
        """

        client = AsyncClient()
        response = await client.get(self._props["avatar"])  # type: ignore
        return response.content


class ChattableUser(User, ChattableModel[UserMessage]):
    """
    可聊天用户。

    指示可以发送消息的用户。
    """

    _dms: DirectMessageSubject

    def __init__(self, user: User, dms: DirectMessageSubject) -> None:
        """
        初始化 `ChattableUser` 实例。

        参数：
            - bot: 用户所属机器人
            - props: 属性
            - dms: `DirectMessageSubject` 实例
        """

        super().__init__(user._bot, user._props)
        self._dms = dms

    async def reply(self, target: UserMessage, *message: Sendable) -> UserMessage:
        from cyan.model.message import create_message_content

        return await self._send(create_message_content(*message), target)

    async def send(self, *message: Sendable) -> UserMessage:
        """
        异步发送消息。

        参数：
            - message: 将要发送的消息

        返回：
            返回表示以 `UserMessage` 类型表示的所发送消息。
        """

        from cyan.model.message import create_message_content

        return await self._send(create_message_content(*message), None)

    async def get_message(self, identifier: str) -> UserMessage:
        response = await self.bot.get(f"/channels/{self._dms.channel}/messages/{identifier}")
        message = response.json()
        return UserMessage.parse(self.bot, message)

    async def _send(
        self,
        message: MessageContent,
        replying_target: Optional[UserMessage]
    ) -> UserMessage:
        from cyan.model.message import MessageContent

        content = MessageContent(message).to_dict()
        if replying_target:
            content["msg_id"] = replying_target.identifier
        response = await self.bot.post(f"/dms/{self._dms.guild}/messages", content=content)
        data: Dict[str, Any] = response.json()
        return UserMessage.parse(self.bot, data)
