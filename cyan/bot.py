from dataclasses import dataclass
from types import TracebackType
from typing import Any
from urllib.parse import urljoin
from httpx import AsyncClient, Response

from cyan.exception import OpenApiError, InvalidTargetError

# 参考 https://bot.q.qq.com/wiki/develop/api/openapi/user/guilds.html。
_GUILD_QUERY_LIMIT = 100


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

    def __init__(self, api_base_url: str, ticket: Ticket):
        """
        初始化 `Bot` 实例。

        参数：
            - api_base_url: API 地址（包括 schema, host, port）
            - ticket: 票据
        """

        self._base_url = api_base_url
        headers = {"Authorization": f"Bot {ticket.app_id}.{ticket.token}"}
        self._client = AsyncClient(headers=headers)

    async def get(self, path: str, params: dict[str, Any] | None = None):
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

    async def post(self, path: str, params: dict[str, Any] | None = None):
        """
        异步向服务器请求 POST 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.post(url, params=params)  # type: ignore
        return Bot._check_error(response)

    async def put(self, path: str, params: dict[str, Any] | None = None):
        """
        异步向服务器请求 PUT 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.put(url, params=params)  # type: ignore
        return Bot._check_error(response)

    async def delete(self, path: str, params: dict[str, Any] | None = None):
        """
        异步向服务器请求 DELETE 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - params: 请求参数

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.delete(url, params=params)  # type: ignore
        return Bot._check_error(response)

    async def patch(self, path: str, params: dict[str, Any] | None = None):
        """
        异步向服务器请求 PATCH 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - content: 请求内容

        返回：
            以 `Response` 类型表示的服务器响应。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.patch(url, params=params)  # type: ignore
        return Bot._check_error(response)

    async def aclose(self):
        """
        异步关闭当前机器人。
        """

        await self._client.aclose()

    async def get_current_user(self):
        """
        异步获取当前机器人用户。

        返回：
            以 `User` 类型表示的当前用户。
        """

        from cyan.model.user import User

        response = await self.get("/users/@me")
        user = response.json()
        user["bot"] = True
        return User(user)

    async def get_guild(self, identifier: str):
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

    async def get_guilds(self):
        """
        异步获取当前机器人的所有频道。

        返回：
            以 `Guild` 类型表示频道的 `list` 集合。
        """

        from cyan.model.guild import Guild

        cur = None
        guilds = list[Guild]()
        while True:
            params: dict[str, Any] = {"limit": _GUILD_QUERY_LIMIT}
            params.update(
                {"after": cur} if cur else {}
            )
            response = await self.get("/users/@me/guilds", params)
            content = response.json()
            guilds.extend([Guild(self, guild) for guild in content])
            if len(content) < _GUILD_QUERY_LIMIT:
                return guilds
            cur = guilds[-1].identifier

    async def get_channel(self, identifier: str):
        """
        异步获取指定 ID 子频道。

        参数：
            - identifier: 频道 ID

        返回：
            以 `Channel` 类型表示的子频道。
        """

        from cyan.model.channel import Channel

        channel = await self._get_channel_core(identifier)
        if isinstance(channel, Channel):
            return channel
        raise InvalidTargetError("指定的 ID 不为子频道。")

    async def get_channel_group(self, identifier: str):
        """
        异步获取指定 ID 子频道。

        参数：
            - identifier: 频道 ID

        返回：
            以 `Channel` 类型表示的子频道。
        """

        from cyan.model.channel import ChannelGroup

        channel = await self._get_channel_core(identifier)
        if isinstance(channel, ChannelGroup):
            return channel
        raise InvalidTargetError("指定的 ID 不为子频道组。")

    async def _get_channel_core(self, identifier: str):
        """
        异步获取指定 ID 子频道或子频道组。

        参数：
            - identifier: 频道 ID

        返回：
            以 `Channel` 类型表示的子频道或以 `ChannelGroup` 类型表示的子频道组。
        """

        from cyan.model.channel import parse as parse_channel

        response = await self.get(f"/channels/{identifier}")
        return parse_channel(self, response.json())

    @staticmethod
    def _check_error(response: Response):
        """
        从服务器响应中检查错误。

        返回：
            传入的 `response` 参数。
        """
        if int(response.status_code / 10) != 20:  # type: ignore
            content = response.json()
            raise OpenApiError(
                response.status_code,  # type: ignore
                content["code"],
                content["message"]
            )
        return response

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] = ...,
        exc_value: BaseException = ...,
        traceback: TracebackType = ...
    ):
        await self.aclose()
