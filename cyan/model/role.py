from typing import TYPE_CHECKING, Any, Dict, Optional

from cyan.bot import Bot
from cyan.color import ARGB
from cyan.exception import InvalidOperationError
from cyan.model.guild import Guild
from cyan.model import Model
from cyan.model.renovatable import AsyncRenovatable

if TYPE_CHECKING:
    from cyan.model.member import Member


class DefaultRoleId:
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
    所有者。
    """

    OPERATOR = "5"
    """
    子频道管理员。
    """


class Role(Model, AsyncRenovatable["Role"]):
    """
    身份组。
    """

    _bot: Bot
    _guild: Guild
    _props: Dict[str, Any]

    def __init__(self, bot: Bot, guild: Guild, props: Dict[str, Any]) -> None:
        """
        初始化 `Role` 实例。

        参数：
            - bot: 身份组所属机器人
            - guild: 身份组所属频道
            - props: 属性
        """

        self._bot = bot
        self._guild = guild
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
    def color(self) -> ARGB:
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
    def guild(self) -> Guild:
        """
        身份组所属频道。
        """

        return self._guild

    async def set_name(self, name: str) -> None:
        """
        异步修改身份组名称。

        参数：
            - name: 目标名称
        """

        await self._modify(name=name)

    async def set_color(self, color: ARGB) -> None:
        """
        异步修改身份组颜色。

        参数：
            - color: 目标颜色
        """

        await self._modify(color=color.to_hex())

    async def show(self) -> None:
        """
        异步启用身份组在成员列表中的单独展示。
        """

        await self._modify(shown=True)

    async def hide(self) -> None:
        """
        异步关闭身份组在成员列表中的单独展示。
        """

        await self._modify(shown=False)

    async def add(self, member: "Member") -> None:
        """
        异步添加成员到当前身份组。

        参数：
            - member: 将要添加到当前身份组的成员
        """

        if self.identifier == DefaultRoleId.OPERATOR:
            raise InvalidOperationError(
                "“子频道管理员”身份组不支持添加成员，如需设置子频道管理员请调用 Channel.add_operator 方法。"
            )
        if self.identifier == DefaultRoleId.ADMINISTRATOR:
            raise InvalidOperationError(
                "“管理员”身份组不支持添加成员，如需移除管理员请调用 Guild.add_administrator 方法。"
            )

        await self.bot.put(
            f"/guilds/{self.guild.identifier}/members/{member.identifier}/roles/{self.identifier}"
        )

    async def remove(self, member: "Member") -> None:
        """
        异步从当前身份组移除指定成员。

        参数：
            - member: 将要从当前身份组移除的成员
        """

        if self.identifier == DefaultRoleId.OPERATOR:
            raise InvalidOperationError(
                "“子频道管理员”身份组不支持移除成员，如需移除子频道管理员请调用 Channel.remove_operator 方法。"
            )
        if self.identifier == DefaultRoleId.ADMINISTRATOR:
            raise InvalidOperationError(
                "“管理员”身份组不支持移除成员，如需移除管理员请调用 Guild.remove_administrator 方法。"
            )

        await self.bot.delete(
            f"/guilds/{self.guild.identifier}/members/{member.identifier}/roles/{self.identifier}"
        )

    async def _modify(
        self,
        name: Optional[str] = None,
        color: Optional[int] = None,
        shown: Optional[bool] = None
    ) -> None:
        _filter = {
            "name": int(name is not None),
            "color": int(color is not None),
            "hoist": int(shown is not None)
        }
        info = {"name": name, "color": color, "hoist": int(bool(shown))}
        content = {"filter": _filter, "info": info}
        response = await self.bot.patch(
            f"/guilds/{self.guild.identifier}/roles/{self.identifier}",
            content=content
        )
        self._props = response.json()["role"]

    async def renovate(self) -> "Role":
        guild = await self.guild.renovate()
        return await guild.get_role(self.identifier)
