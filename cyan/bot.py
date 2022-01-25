from dataclasses import dataclass
from types import TracebackType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union
from urllib.parse import urljoin
from httpx import AsyncClient, Response

from cyan.exception import OpenApiError, InvalidTargetError

if TYPE_CHECKING:
    from cyan.event import EventSource
    from cyan.model.user import User
    from cyan.model.guild import Guild
    from cyan.model.channel import Channel, ChannelGroup

# 参考 https://bot.q.qq.com/wiki/develop/api/openapi/user/guilds.html。
_GUILD_QUERY_LIMIT: int = 100


@dataclass
class Ticket:
    """
    票据。
    """

    app_id: str
    """
    用于指示机器人的 ID。
    """

    token: str
    """
    机器人 Token。
    """


class Bot:
    """
    机器人。
    """

    _base_url: str
    _client: AsyncClient
    _event_source: "EventSource"

    def __init__(self, api_base_url: str, ticket: Ticket) -> None:
        """
        初始化 `Bot` 实例。

        参数：
            - api_base_url: API 地址（包括 schema, host, port）
            - ticket: 票据
        """

        from cyan.event import EventSource

        self._base_url = api_base_url
        authorization = f"Bot {ticket.app_id}.{ticket.token}"
        headers = {"Authorization": authorization}
        self._client = AsyncClient(headers=headers)
        self._event_source = EventSource(self, authorization)

    @property
    def event_source(self) -> "EventSource":
        """
        事件源。
        """

        return self._event_source

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Response:
        """
        异步向服务器请求 GET 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.get(url, params=params)  # type: ignore
        return Bot._check_error(response)

    async def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        content: Any = None
    ) -> Response:
        """
        异步向服务器请求 POST 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数
            - content: 请求内容（将序列化为 JSON）

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.post(url, params=params, json=content)  # type: ignore
        return Bot._check_error(response)

    async def put(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        content: Any = None
    ) -> Response:
        """
        异步向服务器请求 PUT 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数
            - content: 请求内容（将序列化为 JSON）

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.put(url, params=params, json=content)  # type: ignore
        return Bot._check_error(response)

    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        content: Any = None
    ) -> Response:
        """
        异步向服务器请求 DELETE 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数
            - content: 请求内容（将序列化为 JSON）

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.request(  # type: ignore
            "DELETE", url, params=params, json=content
        )
        return Bot._check_error(response)

    async def patch(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        content: Any = None
    ) -> Response:
        """
        异步向服务器请求 PATCH 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数
            - content: 请求内容（将序列化为 JSON）

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.patch(url, params=params, json=content)  # type: ignore
        return Bot._check_error(response)

    async def aclose(self) -> None:
        """
        异步关闭当前机器人。
        """

        if self._event_source.connected:
            await self._event_source.disconnect()
        await self._client.aclose()

    async def get_current_user(self) -> "User":
        """
        异步获取当前机器人用户。

        返回：
            以 `User` 类型表示的当前用户。
        """

        from cyan.model.user import User

        response = await self.get("/users/@me")
        user = response.json()
        user["bot"] = True
        return User(self, user)

    async def get_guild(self, identifier: str) -> "Guild":
        """
        异步获取指定 ID 频道。

        参数：
            - identifier: 频道 ID

        返回：
            以 `Guild` 类型表示的频道。
        """

        from cyan.model.guild import Guild

        response = await self.get(f"/guilds/{identifier}")
        return Guild(self, response.json())

    async def get_guilds(self) -> List["Guild"]:
        """
        异步获取当前机器人的所有频道。

        返回：
            以 `Guild` 类型表示频道的 `list` 集合。
        """

        from cyan.model.guild import Guild

        cur = None
        guilds: List[Guild] = []
        while True:
            params: Dict[str, Any] = {"limit": _GUILD_QUERY_LIMIT}
            if cur:
                params["after"] = cur
            response = await self.get("/users/@me/guilds", params)
            content = response.json()
            guilds.extend([Guild(self, guild) for guild in content])
            if len(content) < _GUILD_QUERY_LIMIT:
                return guilds
            cur = guilds[-1].identifier

    async def get_channel(self, identifier: str) -> "Channel":
        """
        异步获取指定 ID 子频道。

        参数：
            - identifier: 子频道 ID

        返回：
            以 `Channel` 类型表示的子频道。
        """

        from cyan.model.channel import Channel

        channel = await self._get_channel_core(identifier)
        if isinstance(channel, Channel):
            return channel
        raise InvalidTargetError("指定的 ID 不为子频道。")

    async def get_channel_group(self, identifier: str) -> "ChannelGroup":
        """
        异步获取指定 ID 子频道。

        参数：
            - identifier: 频道组 ID

        返回：
            以 `Channel` 类型表示的子频道。
        """

        from cyan.model.channel import ChannelGroup

        channel = await self._get_channel_core(identifier)
        if isinstance(channel, ChannelGroup):
            return channel
        raise InvalidTargetError("指定的 ID 不为子频道组。")

    async def _get_channel_core(self, identifier: str) -> Union["Channel", "ChannelGroup"]:
        from cyan.model.channel import parse as parse_channel

        response = await self.get(f"/channels/{identifier}")
        return await parse_channel(self, response.json())

    @staticmethod
    def _check_error(response: Response) -> Response:
        if int(response.status_code / 10) != 20:  # type: ignore
            content = response.json()
            raise OpenApiError(
                response.status_code,  # type: ignore
                content["code"],
                content["message"]
            )
        return response

    async def __aenter__(self) -> "Bot":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] = ...,
        exc_value: BaseException = ...,
        traceback: TracebackType = ...
    ) -> None:
        await self.aclose()
