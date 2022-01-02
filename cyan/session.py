import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin
from httpx import AsyncClient, Response

from cyan.exception import ApiError
from cyan.model import User


@dataclass
class Ticket:
    """
    票据。

    属性：
        - app_id: 用于指示机器人的 ID
        - token: 机器人 Token
    """

    app_id: str
    token: str


class Session:
    """
    会话。
    """

    _base_url: str
    _client: AsyncClient

    def __init__(self, api_base_url: str, ticket: Ticket):
        """
        初始化 `Session` 实例。

        参数：
            - api_base_url: API 地址（包括 schema, host, port）
            - ticket: 票据
        """

        self._base_url = api_base_url
        headers = {"Authorization": f"Bot {ticket.app_id}.{ticket.token}"}
        self._client = AsyncClient(headers=headers)

    async def get(self, path: str):
        """
        异步向服务器请求 GET 操作。

        参数：
            - path: 请求路径（不包含 API 地址）

        返回：
            反序列化后的服务器返回内容。
        """

        url = urljoin(self._base_url, path)
        response = await self._client.get(url)  # type: ignore
        return Session._check_error(response).json()

    async def post(self, path: str, content: Any = None):
        """
        异步向服务器请求 POST 操作。

        参数：
            - path: 请求路径（不包含 API 地址）
            - content: 请求内容

        返回：
            反序列化后的服务器返回内容。
        """

        url = urljoin(self._base_url, path)
        json_content = json.dumps(content)
        response = await self._client.post(  # type: ignore
            url,
            content=json_content
        )
        return Session._check_error(response).json()

    async def close(self):
        """
        关闭会话。
        """
        await self._client.aclose()

    async def get_current_user(self):
        """
        异步获取当前会话用户。

        返回：
            以 `User` 类型表示的当前用户。
        """
        props = await self.get("/users/@me")
        props["bot"] = True
        return User(props)

    @staticmethod
    def _check_error(response: Response):
        """
        从服务器响应中检查错误。

        返回：
            传入的 `response` 参数。
        """
        if int(response.status_code / 10) != 20:  # type: ignore
            content = response.json()
            raise ApiError(content["code"], content["message"])
        return response
