from abc import abstractmethod
from typing import Any, Generic, Union, TypeVar, TYPE_CHECKING

from cyan.bot import Bot

if TYPE_CHECKING:
    from cyan.model.message import Message, MessageAuditInfo, Sendable


_T_Message = TypeVar("_T_Message", bound="Message")  # type: ignore


class ChattableModel(Generic[_T_Message]):
    """
    可聊天 `Model`。

    指示机器人可以发送消息的 `Model`。
    """

    async def reply(self, target: _T_Message, *message: "Sendable") -> _T_Message:
        """
        异步回复指定消息。

        参数：
            - target: 将要被回复的消息
            - message: 回应消息

        返回：
            返回表示以 `Message` 类型表示的所发送消息。
        """

        raise NotImplementedError

    async def send(self, *message: "Sendable") -> Union[_T_Message, "MessageAuditInfo"]:
        """
        异步发送消息。

        参数：
            - message: 将要发送的消息

        返回：
            当消息需被审核时返回以 `MessageAuditInfo` 类型表示的消息审核信息；
            否则，返回表示以 `Message` 类型表示的所发送消息。
        """

        raise NotImplementedError

    async def get_message(self, identifier: str) -> _T_Message:
        """
        异步获取指定 ID 消息。

        参数：
            - identifier: 消息 ID

        返回：
            以 `Message` 类型表示的消息。
        """

        raise NotImplementedError


class Model:
    """
    Model。
    """

    @property
    @abstractmethod
    def bot(self) -> Bot:
        """
        `Model` 所属机器人。
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        `Model` ID。
        """
        raise NotImplementedError

    def __eq__(self, obj: Any) -> bool:
        _type = type(self)
        return isinstance(obj, _type) and obj.bot == self.bot and obj.identifier == self.identifier

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.identifier})"


from .announcement import *
from .user import *
from .guild import *
from .member import *
from .role import *
from .channel import *
from .schedule import *
from .message import MessageContent as MessageContent
from .message import MessageAuditInfo as MessageAuditInfo
from .message import MessageElement as MessageElement
from .message.message import *
