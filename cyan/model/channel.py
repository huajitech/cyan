from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from cyan.constant import DEFAULT_ID
from cyan.bot import Bot
from cyan.exception import InvalidOperationError, OpenApiError
from cyan.model.announcement import Announcement
from cyan.model.guild import Guild
from cyan.model import ChattableModel, Model
from cyan.model.member import Member
from cyan.model.message.message import ChannelMessage
from cyan.model.renovatable import AsyncRenovatable
from cyan.model.role import DefaultRoleId
from cyan.model.schedule import Schedule, RemindType
from cyan.util._enum import get_enum_key


class TextChannelType(Enum):
    """
    文字子频道类型。
    """

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


class AppChannelType(Enum):
    """
    应用子频道类型。
    """

    HONOR_OF_KINGS = 1000000
    """
    王者开黑大厅。
    """

    GAME = 1000001
    """
    互动小游戏。
    """

    VOTE = 1000010
    """
    腾讯投票。
    """

    QQ_SPEED = 1000051
    """
    QQ 飞车开黑大厅。
    """

    SCHEDULE = 1000050
    """
    日程提醒。
    """

    CODM = 1000070
    """
    CoDM 开黑大厅。
    """

    GAME_FOR_PEACE = 1010000
    """
    和平精英开黑大厅。
    """


class ChannelVisibility(Enum):
    """
    子频道可见性。
    """

    EVERYONE = 0
    """
    所有人。
    """

    ADMINISTRATOR = 1
    """
    所有者及管理员。
    """

    APOINTEE = 2
    """
    所有者、管理员及指定人员。
    """


class ChannelPermission(Enum):
    """
    子频道权限。
    """

    DEFAULT = 0
    """
    默认。
    """

    EVERYONE = 1
    """
    所有人。
    """

    APOINTEE = 2
    """
    所有者、管理员及指定人员。
    """


class ChannelGroup(Model, AsyncRenovatable["ChannelGroup"]):
    """
    子频道组。
    """

    _props: Dict[str, Any]
    _guild: Guild
    _bot: Bot

    def __init__(self, bot: Bot, guild: Guild, props: Dict[str, Any]) -> None:
        """
        初始化 `ChannelGroup` 实例。

        参数：
            - bot: 子频道组所属机器人
            - guild: 子频道组所属频道
            - props: 属性
        """

        self._props = props
        self._guild = guild
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
        子频道组名。
        """

        return self._props["name"]

    @property
    def guild(self) -> Guild:
        """
        子频道组附属频道。
        """

        return self._guild

    @property
    def visibility(self) -> ChannelVisibility:
        """
        子频道组可见性。
        """

        return ChannelVisibility(self._props["private_type"])

    async def get_owner(self) -> Optional[Member]:
        """
        获取子频道组所有者。

        返回：
            当存在子频道组所有者时，返回以 `Member` 类型表示的当前子频道所有者；
            若不存在，则返回 `None`。
        """

        identifier = self._props["owner_id"]
        if identifier == DEFAULT_ID:
            return None
        try:
            return await self.guild.get_member(identifier)
        except OpenApiError as ex:
            if ex.code == 50001:
                return None
            raise

    async def get_children(self) -> List["Channel"]:
        """
        获取子频道组的成员。

        返回：
            以 `Channel` 类型表示成员子频道的 `list` 集合。
        """

        channels = await self.guild.get_channels()
        return [
            channel
            for channel in channels
            if channel.is_child_of(self)
        ]

    async def renovate(self) -> "ChannelGroup":
        return await self.bot.get_channel_group(self.identifier)


class Channel(Model, AsyncRenovatable["Channel"]):
    """
    子频道。
    """

    _props: Dict[str, Any]
    _guild: Guild
    _bot: Bot

    def __init__(self, bot: Bot, guild: Guild, props: Dict[str, Any]) -> None:
        """
        初始化 `Channel` 实例。

        参数：
            - bot: 子频道所属机器人
            - guild: 子频道所属频道
            - props: 属性
        """

        self._props = props
        self._guild = guild
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
        子频道名。
        """

        return self._props["name"]

    @property
    def guild(self) -> Guild:
        """
        子频道附属频道。
        """

        return self._guild

    @property
    def visibility(self) -> ChannelVisibility:
        """
        子频道可见性。
        """

        return ChannelVisibility(self._props["private_type"])

    @property
    def permission(self) -> ChannelPermission:
        """
        子频道权限。
        """

        return ChannelPermission(self._props["speak_permission"])

    async def get_owner(self) -> Optional[Member]:
        """
        异步获取子频道所有者。

        返回：
            当存在子频道所有者时，返回以 `Member` 类型表示的当前子频道所有者；
            若不存在，则返回 `None`。
        """

        identifier = self._props["owner_id"]
        if identifier == DEFAULT_ID:
            return None
        try:
            return await self.guild.get_member(identifier)
        except OpenApiError as ex:
            if ex.code == 50001:
                return None
            raise

    async def get_parent(self) -> ChannelGroup:
        """
        异步获取子频道附属的子频道组。

        返回：
            以 `Channel` 类型表示的当前子频道附属的子频道组。
        """

        return await self.bot.get_channel_group(self._props["parent_id"])

    def is_child_of(self, parent: ChannelGroup) -> bool:
        """
        判断当前子频道是否为指定子频道组的成员。

        参数：
            - parent: 将要用于判断是否为附属子频道的指定子频道组

        返回：
            如果当前子频道为指定子频道组的成员，返回 `True`；否则，返回 `False`。
        """

        return self._props["parent_id"] == parent.identifier

    async def add_operator(self, member: Member) -> None:
        """
        异步添加管理员到当前子频道。

        参数：
            - member: 将要添加到当前子频道的成员
        """

        channel = {"id": self.identifier}
        await self.bot.put(
            f"/guilds/{self.guild.identifier}/members/{member.identifier}"
            f"/roles/{DefaultRoleId.OPERATOR}",
            content={"channel": channel}
        )

    async def remove_operator(self, member: Member) -> None:
        """
        异步从当前子频道移除指定管理员。

        参数：
            - member: 将要从当前子频道移除的管理员
        """

        channel = {"id": self.identifier}
        await self.bot.delete(
            f"/guilds/{self.guild.identifier}/members/{member.identifier}"
            f"/roles/{DefaultRoleId.OPERATOR}",
            content={"channel": channel}
        )

    async def renovate(self) -> "Channel":
        return await self.bot.get_channel(self.identifier)


class TextChannel(Channel, ChattableModel[ChannelMessage]):
    """
    文字子频道。
    """

    from cyan.model.message import MessageAuditInfo, MessageContent, Sendable

    @property
    def text_channel_type(self) -> Union[TextChannelType, int]:
        """
        文字子频道类型。

        当类型值在 `TextChannelType` 中时为对应 `TextChannelType`；
        否则为指示当前文字子频道类型的 `int` 值。
        """

        return get_enum_key(TextChannelType, self._props["sub_type"])

    async def reply(self, target: ChannelMessage, *message: Sendable) -> ChannelMessage:
        from cyan.model.message import create_message_content

        result = await self._send(create_message_content(*message), target)
        assert isinstance(result, ChannelMessage)
        return result

    async def send(self, *message: Sendable) -> Union[MessageAuditInfo, ChannelMessage]:
        from cyan.model.message import create_message_content

        return await self._send(create_message_content(*message), None)

    async def get_message(self, identifier: str) -> ChannelMessage:
        response = await self.bot.get(f"/channels/{self.identifier}/messages/{identifier}")
        message = response.json()
        return ChannelMessage.parse(self.bot, message)

    async def _send(
        self,
        message: MessageContent,
        replying_target: Optional[ChannelMessage]
    ) -> Union[MessageAuditInfo, ChannelMessage]:
        from cyan.model.message import MessageContent, MessageAuditInfo

        content = MessageContent(message).to_dict()
        if replying_target:
            content["msg_id"] = replying_target.identifier
        response = await self.bot.post(f"/channels/{self.identifier}/messages", content=content)
        data: Dict[str, Any] = response.json()
        code = data.get("code", None)
        if code == 304023 or code == 304024:
            return MessageAuditInfo(self.bot, data)
        return ChannelMessage.parse(self.bot, data)

    async def announce(self, message: ChannelMessage) -> Announcement:
        """
        异步在当前子频道公告指定消息。

        参数：
            - message: 将要在当前子频道公告的消息

        返回：
            以 `Announcement` 类型表示的公告。
        """

        content = {"message_id": message.identifier}
        response = await self.bot.post(
            f"/channels/{self.identifier}/announces",
            content=content
        )
        announcement = response.json()
        return Announcement(self.bot, announcement)

    async def recall_announcement(self) -> None:
        """
        异步撤销当前子频道的公告。
        """

        await self.bot.delete(f"/channels/{self.identifier}/announces/all")


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

    @property
    def app_channel_type(self) -> Union[AppChannelType, int]:
        """
        应用子频道类型。

        当类型值在 `AppChannelType` 中时为对应 `AppChannelType`；
        否则为指示当前应用子频道类型的 `int` 值。
        """

        return get_enum_key(AppChannelType, int(self._props["application_id"]))


class ScheduleChannel(AppChannel):
    """
    日程子频道。
    """

    @staticmethod
    def from_app_channel(channel: AppChannel) -> "ScheduleChannel":
        """
        转换 `AppChannel` 实例为 `ScheduleChannel` 实例。

        参数：
            - channel: 所需转换的应用子频道（应用子频道类型必须为日程提醒）

        返回：
            以 `ScheduleChannel` 类型表示等效于被转换应用子频道的日程子频道。
        """

        if channel.app_channel_type == AppChannelType.SCHEDULE:
            return ScheduleChannel(channel.bot, channel.guild, channel._props)
        raise InvalidOperationError("目标应用子频道类型不为日程提醒。")

    # TODO: 实现为获取所有日程（通过传入指定 since 参数以实现，但据目前所提供的 API 下测试失败）。
    # 参考 https://bot.q.qq.com/wiki/develop/api/openapi/schedule/get_schedules.html。
    async def get_schedules(self) -> List[Schedule]:
        """
        异步获取子频道当天日程列表。

        返回：
            以 `Schedule` 类型表示日程的 `list` 集合。
        """

        response = await self.bot.get(f"/channels/{self.identifier}/schedules")
        schedules = response.json()
        return (
            [Schedule(self.bot, self, schedule) for schedule in schedules]
            if schedules else []
        )

    async def get_schedule(self, identifier: str) -> Schedule:
        """
        异步获取子频道的指定 ID 日程。

        参数：
            - identifier: 日程 ID

        返回：
            以 `Schedule` 类型表示的日程。
        """

        response = await self.bot.get(f"/channels/{self.identifier}/schedules/{identifier}")
        schedule = response.json()
        return Schedule(self.bot, self, schedule)

    async def create_schedule(
        self,
        name: str,
        start_time: datetime,
        end_time: datetime,
        remind_type: RemindType = RemindType.SILENT,
        description: str = "",
        destination: Optional[Channel] = None
    ) -> Schedule:
        """
        异步在当前子频道创建日程。

        参数：
            - name: 日程名称
            - start_time: 日程开始时间
            - end_time: 日程结束时间
            - remind_type: 提醒类型
            - description: 日程描述
            - destination: 日程指向目标子频道

        返回：
            以 `Schedule` 类型表示的日程。
        """

        schedule = {
            "name": name,
            "description": description,
            "start_timestamp": str(int(start_time.timestamp() * 1000)),
            "end_timestamp": str(int(end_time.timestamp() * 1000)),
            "jump_channel_id": destination.identifier if destination else DEFAULT_ID,
            "remind_type": str(remind_type.value)
        }
        content = {"schedule": schedule}
        response = await self.bot.post(f"/channels/{self.identifier}/schedules", content=content)
        return Schedule(self.bot, self, response.json())


class ForumChannel(Channel):
    """
    论坛子频道。
    """

    pass


class UnknownChannel(Channel):
    """
    未知子频道。
    """

    @property
    def channel_type(self) -> int:
        """
        子频道类型。
        """

        return self._props["type"]


_CHANNEL_TYPE_MAPPING = {
    0: TextChannel,
    # 1: Reserved,
    2: VoiceChannel,
    # 3: Reserved,
    4: ChannelGroup,
    10005: LiveChannel,
    10006: AppChannel,
    10007: ForumChannel
}


async def parse(
    bot: Bot,
    _dict: Dict[str, Any],
    guild: Optional[Guild] = None
) -> Union[Channel, ChannelGroup]:
    """
    解析子频道信息字典为 `Channel` 或 `ChannelGroup` 类型。

    参数：
        - _dict: 将用于解析的字典
        - guild: 目标的附属频道

    返回：
        当子频道类型为子频道组时返回以 `ChannelGroup` 类型表示的子频道组，否则返回以 `Channel` 类型表示的子频道。
    """

    channel_type = _CHANNEL_TYPE_MAPPING.get(_dict["type"], UnknownChannel)
    guild = guild or await bot.get_guild(_dict["guild_id"])
    return channel_type(bot, guild, _dict)
