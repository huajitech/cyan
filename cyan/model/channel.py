from enum import Enum
from typing import Any

from cyan.constant import DEFAULT_ID
from cyan.session import Session
from cyan.utils.enum import get_enum_key


class TextChannelType(Enum):
    CHAT = 0
    """
    闲聊。
    """

    ANNOUNCEMENT = 1
    """
    公告。
    """

    STRATEGY = 2
    """
    攻略。
    """

    GAME = 3
    """
    开黑。
    """


class ChannelVisibility(Enum):
    EVERYONE = 0
    """
    所有人。
    """

    ADMINISTRATOR = 1
    """
    创建者及管理员。
    """

    APOINTEE = 2
    """
    创建者、管理员及指定人员。
    """


class ChannelGroup:
    """
    子频道组。
    """

    _props: dict[str, Any]
    _session: Session

    def __init__(self, session: Session, props: dict[str, Any]):
        """
        初始化 `Guild` 实例。

        参数：
            - session: 会话
            - props: 属性
        """

        self._props = props
        self._session = session

    @property
    def identifier(self) -> str:
        """
        子频道组 ID。
        """

        return self._props["id"]

    @property
    def name(self) -> str:
        """
        子频道组名。
        """

        return self._props["name"]

    @property
    def visibility(self):
        """
        子频道组可见性。
        """

        return ChannelVisibility(self._props["private_type"])

    async def get_owner(self):
        """
        获取子频道组创建者。

        返回：
            当存在子频道组创建者时，返回以 `Member` 类型表示的当前子频道创建者；
            若不存在，则返回 None。
        """

        identifier = self._props["owner_id"]
        if identifier == DEFAULT_ID:
            return None
        guild = await self.get_guild()
        return await guild.get_member(identifier)

    async def get_guild(self):
        """
        获取子频道组附属的频道。

        返回：
            以 `Guild` 类型表示的当前子频道附属的频道。
        """

        return await self._session.get_guild(self._props["guild_id"])

    async def get_children(self):
        """
        获取子频道组的成员。

        返回：
            以 `Channel` 类型表示成员子频道的 `list` 集合。
        """

        guild = await self.get_guild()
        channels = await guild.get_channels()
        return [
            channel
            for channel in channels
            if channel.is_child_of(self)
        ]


class Channel:
    """
    子频道。
    """

    _props: dict[str, Any]
    _session: Session

    def __init__(self, session: Session, props: dict[str, Any]):
        """
        初始化 `Guild` 实例。

        参数：
            - session: 会话
            - props: 属性
        """

        self._props = props
        self._session = session

    @property
    def identifier(self) -> str:
        """
        子频道 ID。
        """

        return self._props["id"]

    @property
    def name(self) -> str:
        """
        子频道名。
        """

        return self._props["name"]

    @property
    def visibility(self):
        """
        子频道可见性。
        """

        return ChannelVisibility(self._props["private_type"])

    async def get_owner(self):
        """
        获取子频道组创建者。

        返回：
            当存在子频道组创建者时，返回以 `Member` 类型表示的当前子频道创建者；
            若不存在，则返回 None。
        """

        identifier = self._props["owner_id"]
        if identifier == DEFAULT_ID:
            return None
        guild = await self.get_guild()
        return await guild.get_member(identifier)

    async def get_parent(self):
        """
        获取子频道附属的子频道组。

        返回：
            以 `Channel` 类型表示的当前子频道附属的子频道组。
        """

        return await self._session.get_channel_group(self._props["parent_id"])

    async def is_child_of(self, parent: ChannelGroup):
        """
        判断当前子频道是否为指定子频道组的成员。

        返回：
            如果当前子频道为指定子频道组的成员，返回 `True`；否则，返回 `False`。
        """
        return self._props["parent_id"] == parent.identifier

    async def get_guild(self):
        """
        获取子频道附属的频道。

        返回：
            以 `Guild` 类型表示的当前子频道附属的频道。
        """

        return await self._session.get_guild(self._props["guild_id"])


class TextChannel(Channel):
    @property
    def text_channel_type(self):
        """
        文字频道类型。
        """

        return get_enum_key(TextChannelType, self._props["sub_type"])


class VoiceChannel(Channel):
    """
    语音子频道。
    """

    pass


class LiveChannel(Channel):
    """
    直播子频道。
    """

    pass


class AppChannel(Channel):
    """
    应用子频道。
    """

    pass


class ForumChannel(Channel):
    """
    论坛子频道。
    """

    pass


class UnknownChannel(Channel):
    @property
    def channel_type(self):
        """
        子频道类型。
        """

        return get_enum_key(TextChannelType, self._props["type"])


CHANNEL_TYPE_MAPPING = {
    0: TextChannel,
    # 1: Reserved,
    2: VoiceChannel,
    # 3: Reserved,
    4: ChannelGroup,
    10005: LiveChannel,
    10006: AppChannel,
    10007: ForumChannel
}


def parse(session: Session, d: dict[str, Any]) -> Channel | ChannelGroup:
    """
    解析子频道信息字典为 `Channel` 或 `ChannelGroup` 类型。

    返回：
        当子频道类型为子频道组时返回以 `ChannelGroup` 类型表示的子频道组，否则返回以 `Channel` 类型表示的子频道。
    """

    channel_type = CHANNEL_TYPE_MAPPING.get(d["type"], UnknownChannel)
    return channel_type(session, d)
