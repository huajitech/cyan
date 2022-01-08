from enum import Enum
from typing import Any

from cyan.bot import Bot
from cyan.color import ARGB
from cyan.model.guild import Guild


class DefaultRoleId(Enum):
    """
    默认身份组 ID。
    """

    DEFAULT = "1"
    """
    默认。
    """

    ADMINISTRATOR = "2"
    """
    管理员。
    """

    OWNER = "4"
    """
    创建者。
    """

    OPERATOR = "5"
    """
    子频道管理员。
    """


class Role:
    """
    身份组。
    """

    _bot: Bot
    _guild: Guild
    _props: dict[str, Any]

    def __init__(self, bot: Bot, guild: Guild, props: dict[str, Any]):
        """
        初始化 `Role` 实例。

        参数：
            - props: 属性
        """

        self._bot = bot
        self._guild = guild
        self._props = props

    @property
    def identifier(self) -> str:
        """
        身份组 ID。
        """

        return self._props["id"]

    @property
    def name(self) -> str:
        """
        身份组名称。
        """

        return self._props["name"]

    @property
    def capacity(self) -> int:
        """
        身份组容量。
        """

        return self._props["member_limit"]

    @property
    def color(self):
        """
        身份组颜色。
        """

        return ARGB.from_hex(self._props["color"])

    @property
    def shown(self) -> bool:
        """
        身份组是否在成员列表中单独展示。
        """

        return bool(self._props["hoist"])

    @property
    def guild(self):
        """
        身份组所属频道。
        """

        return self._guild

    async def set_name(self, name: str):
        """
        异步修改身份组名称。

        参数：
            - name: 目标名称
        """

        await self._modify(name=name)

    async def set_color(self, color: ARGB):
        """
        异步修改身份组颜色。

        参数：
            - name: 目标颜色
        """

        await self._modify(color=color.to_hex())

    async def show(self):
        """
        异步启用身份组在成员列表中的单独展示。
        """

        await self._modify(shown=True)

    async def hide(self):
        """
        异步关闭身份组在成员列表中的单独展示。
        """

        await self._modify(shown=False)

    async def _modify(
        self,
        name: str | None = None,
        color: int | None = None,
        shown: bool | None = None
    ):
        """
        异步修改身份组信息。

        参数：
            - name: 目标名称
            - color: 目标颜色
            - shown: 是否在成员列表中单独展示
        """

        _filter = {
            "name": int(name is not None),
            "color": int(color is not None),
            "hoist": int(shown is not None)
        }
        info = { "name": name, "color": color, "hoist": int(bool(shown)) }
        content = { "filter": _filter, "info": info }
        response = await self._bot.patch(
            f"/guilds/{self._guild.identifier}/roles/{self.identifier}",
            content=content
        )
        self._props = response.json()["role"]

    async def discard(self):
        """
        异步删除当前身份组。
        """

        await self._bot.delete(f"/guilds/{self.guild.identifier}/roles/{self.identifier}")
