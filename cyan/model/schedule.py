from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from cyan.bot import Bot
from cyan.constant import DEFAULT_ID
from cyan.model import Model
from cyan.model.renovatable import AsyncRenovatable
from cyan.model.user import User


if TYPE_CHECKING:
    from cyan.model.channel import ScheduleChannel, Channel


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


class Schedule(Model, AsyncRenovatable["Schedule"]):
    """
    日程。
    """

    _bot: Bot
    _channel: "ScheduleChannel"
    _props: Dict[str, Any]

    def __init__(self, bot: Bot, channel: "ScheduleChannel", props: Dict[str, Any]) -> None:
        """
        初始化 `Schedule` 实例。

        参数：
            - bot: 日程所属机器人
            - channel: 日程所属频道
            - props: 属性
        """

        self._bot = bot
        self._channel = channel
        self._props = props

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._props["id"]

    @property
    def name(self) -> str:
        """
        日程名称。
        """

        return self._props["name"]

    @property
    def description(self) -> str:
        """
        日程描述。
        """

        return self._props.get("description", None)

    @property
    def start_time(self) -> datetime:
        """
        日程开始时间。
        """

        return datetime.fromtimestamp(int(self._props["start_timestamp"]) / 1000)

    @property
    def end_time(self) -> datetime:
        """
        日程结束时间。
        """

        return datetime.fromtimestamp(int(self._props["end_timestamp"]) / 1000)

    @property
    def channel(self) -> "ScheduleChannel":
        """
        日程所属子频道。
        """

        return self._channel

    @property
    def creator(self) -> User:
        """
        日程创建者。
        """

        return User(self.bot, self._props["creator"]["user"])

    @property
    def remind_type(self) -> RemindType:
        """
        日程提醒类型。
        """
        return RemindType(int(self._props["remind_type"]))

    async def get_destination(self) -> Optional["Channel"]:
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
    async def cancel(self) -> None:
        """
        异步取消当前日程。
        """

        await self.bot.delete(f"/channels/{self.channel.identifier}/schedules/{self.identifier}")

    async def set_name(self, name: str) -> None:
        """
        异步修改日程名称。

        参数：
            - name: 目标名称
        """

        return await self._modify({"name": name})

    async def set_start_time(self, time: datetime) -> None:
        """
        异步修改日程开始时间。

        参数：
            - time: 目标开始时间
        """

        return await self._modify({"start_timestamp": str(int(time.timestamp() * 1000))})

    async def set_end_time(self, time: datetime) -> None:
        """
        异步修改日程结束时间。

        参数：
            - time: 目标结束时间
        """

        return await self._modify({"end_timestamp": str(int(time.timestamp() * 1000))})

    async def set_description(self, description: str) -> None:
        """
        异步修改日程描述。

        参数：
            - description: 目标描述
        """

        return await self._modify({"description": description})

    async def set_destination(self, channel: "Channel") -> None:
        """
        异步修改日程指向的目标子频道。

        参数：
            - channel: 目标子频道
        """

        return await self._modify({"jump_channel_id": channel.identifier})

    async def set_remind_type(self, remind_type: RemindType) -> None:
        """
        异步修改日程提醒类型。

        参数：
            - remind_type: 目标提醒类型
        """

        return await self._modify({"remind_type": str(remind_type.value)})

    async def unset_destination(self) -> None:
        """
        异步取消日程指向目标子频道。
        """

        return await self._modify({"jump_channel_id": DEFAULT_ID})

    async def _modify(self, changes: Dict[str, Any]) -> None:
        schedule = dict(self._props)
        schedule.pop("id")
        schedule.pop("creator")
        schedule.update(changes)
        content = {"schedule": schedule}
        response = await self.bot.patch(
            f"/channels/{self.channel.identifier}/schedules/{self.identifier}",
            content=content
        )
        self._props = response.json()

    async def renovate(self) -> "Schedule":
        from cyan.model.channel import AppChannel, ScheduleChannel

        channel = await self.channel.renovate()
        assert isinstance(channel, AppChannel)
        schedule_channel = ScheduleChannel.from_app_channel(channel)
        return await schedule_channel.get_schedule(self.identifier)
