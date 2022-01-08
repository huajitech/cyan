from datetime import datetime
from enum import Enum
from typing import Any

from cyan.bot import Bot
from cyan.model.guild import Guild
from cyan.model.member import Member


class RemindType(Enum):
    """
    提醒类型。
    """

    SILENT = 0
    """
    不提醒。
    """

    INSTANT = 1
    """
    开始时提醒。
    """

    LATER = 2
    """
    较晚提醒（开始前 5 分钟提醒）。
    """

    LATE = 3
    """
    晚期提醒（开始前 15 分钟提醒）。
    """

    EARLY = 4
    """
    早期提醒（开始前 30 分钟提醒）。
    """

    EARLIER = 5
    """
    较早提醒（开始前 60 分钟提醒）。
    """


class Schedule:
    """
    日程。
    """

    _bot: Bot
    _guild: Guild
    _props: dict[str, Any]

    def __init__(self, bot: Bot, guild: Guild, props: dict[str, Any]):
        """
        初始化 `Schedule` 实例。

        参数：
            - props: 属性
        """

        self._bot = bot
        self._guild = guild
        self._props = props

    @property
    def identifier(self):
        """
        日程 ID。
        """

        return self._props["id"]

    @property
    def name(self):
        """
        日常名称。
        """

        return self._props["name"]

    @property
    def description(self):
        """
        日程描述。
        """

        return self._props.get("description", None)

    @property
    def start_time(self):
        """
        日程开始时间。
        """

        return datetime.fromtimestamp(int(self._props["start_timestamp"]) / 1000)

    @property
    def end_time(self):
        """
        日程结束时间。
        """

        return datetime.fromtimestamp(int(self._props["end_timestamp"]) / 1000)

    @property
    def guild(self):
        """
        日程所属频道。
        """

        return self._guild

    @property
    def creator(self):
        """
        日程创建者。
        """

        return Member(self._bot, self.guild, self._props["creator"])

    @property
    def remind_type(self):
        """
        日程提醒类型。
        """
        return RemindType(int(self._props["remind_type"]))

    async def get_destination(self):
        """
        异步获取日程指向的目标子频道。

        返回：
            以 `Channel` 类型表示的子频道。
        """

        return await self._bot.get_channel(self._props["jump_channel_id"])
