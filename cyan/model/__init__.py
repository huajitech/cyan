from abc import abstractmethod
from typing import Any

from cyan.bot import Bot


class Model:
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


from .announcement import *
from .user import *
from .guild import *
from .member import *
from .role import *
from .channel import *
from .schedule import *
from .message import Message as Message
from .message import MessageContent as MessageContent
from .message import MessageAuditInfo as MessageAuditInfo
from .message import MessageElement as MessageElement
