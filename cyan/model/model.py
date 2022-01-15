from abc import abstractmethod

from cyan.bot import Bot


class Model:
    @property
    @abstractmethod
    def bot(self) -> Bot:
        """
        `Model` 所属机器人实例。
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        `Model` ID。
        """
        raise NotImplementedError
