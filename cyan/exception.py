class CyanException(Exception):
    """
    当 Cyan 出现异常时抛出。
    """

    pass


class InvalidTargetError(Exception):
    """
    当目标无效时抛出。
    """

    pass


class ApiError(CyanException):
    """
    当 API 返回错误时抛出。
    """

    _code: int
    _message: str

    def __init__(self, code: int, message: str):
        """
        初始化 `ApiError` 实例。
        """

        self._code = code
        self._message = message

    @property
    def code(self):
        """
        错误代码。
        """

        return self._code

    @property
    def message(self):
        """
        错误消息。
        """

        return self._message
