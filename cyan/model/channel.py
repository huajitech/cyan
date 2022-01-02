from enum import Enum
from typing import Any

from cyan.session import Session


class ChannelType(Enum):
    TEXT = 0
    """
    文字子频道。
    """
    # RESERVED = 1
    VOICE = 2
    """
    语音子频道。
    """
    # RESERVED = 3
    GROUP = 4
    """
    子频道分组。
    """
    LIVE = 10005
    """
    直播子频道。
    """
    APP = 10006
    """
    应用子频道。
    """
    FORUM = 10007
    """
    论坛子频道。
    """


class ChannelSubType(Enum):
    CHAT = 0
    ANNOUNCEMENT = 1
    STRATEGY = 2
    GAME = 3


class ChannelVisibility(Enum):
    EVERYONE = 0
    ADMINISTRATOR = 1
    APOINTEE = 2


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
    def channel_type(self):
        """
        子频道类型。
        """

        return ChannelType(self._props["type"])

    @property
    def channel_subtype(self):
        """
        子频道子类型。
        """

        return ChannelSubType(self._props["sub_type"])

    @property
    def visibility(self):
        """
        子频道可见性。
        """

        return ChannelVisibility(self._props["private_type"])

    async def get_owner(self):
        """
        获取子频道创建者。

        返回：
            以 `User` 类型表示的当前子频道创建者。
        """

        guild = await self.get_guild()
        member = await guild.get_member(self._props["owner_id"])
        return member.as_user()

    async def get_parent(self):
        """
        获取子频道附属的子频道组。

        返回：
            以 `Channel` 类型表示的当前子频道附属的子频道组。
        """

        return await self._session.get_channel(self._props["parent_id"])

    async def get_guild(self):
        """
        获取子频道附属的频道。

        返回：
            以 `Guild` 类型表示的当前子频道附属的频道。
        """

        return await self._session.get_guild(self._props["guild_id"])
