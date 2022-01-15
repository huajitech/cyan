from datetime import datetime
from enum import Enum
from typing import Any

from cyan.bot import Bot
from cyan.constant import DEFAULT_ID
from cyan.model.member import Member
from cyan.model.channel import Channel
from cyan.model.model import Model


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


class Schedule(Model):
    """
    日程。
    """

    _bot: Bot
    _channel: Channel
    _props: dict[str, Any]

    def __init__(self, bot: Bot, channel: Channel, props: dict[str, Any]):
        """
        初始化 `Schedule` 实例。

        参数：
            - props: 属性
        """

        self._bot = bot
        self._channel = channel
        self._props = props

    @property
    def bot(self):
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["id"]

    @property
    def name(self) -> str:
        return self._props["name"]

    @property
    def description(self) -> str:
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
    def channel(self):
        """
        日程所属子频道。
        """

        return self._channel

    async def get_creator(self):
        """
        异步获取日程创建者。

        返回：
            以 `Member` 类型表示的子频道
        """

        return Member(self.bot, await self.channel.get_guild(), self._props["creator"])

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
            当存在目标子频道时，返回以 `Channel` 类型表示的子频道；若不存在，则返回 `None`。
        """

        if self._props["jump_channel_id"] == DEFAULT_ID:
            return None
        return await self.bot.get_channel(self._props["jump_channel_id"])

    # TODO: 该方法有待测试，据目前所提供的 API 下测试失败。
    # 参考 https://bot.q.qq.com/wiki/develop/api/openapi/schedule/delete_schedule.html。
    async def discard(self):
        """
        异步删除当前日程。
        """

        await self.bot.delete(f"/channels/{self.channel.identifier}/schedules/{self.identifier}")

    # TODO: 实现日程信息修改。
