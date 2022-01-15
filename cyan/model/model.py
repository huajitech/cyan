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

    def __eq__(self, obj: object):
        _type = type(self)
        return isinstance(obj, _type) and obj.bot == self.bot and obj.identifier == self.identifier
