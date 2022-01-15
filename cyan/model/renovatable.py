from abc import abstractmethod
from typing import Generic, TypeVar


_T = TypeVar("_T")


class AsyncRenovatable(Generic[_T]):
    @abstractmethod
    async def renovate(self) -> _T:
        """
        获取更新的实例。
        """

        raise NotImplementedError
