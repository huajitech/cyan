class CyanException(Exception):
    """
    当 Cyan 出现异常时抛出。
    """

    pass


class OperationFailedError(CyanException):
    """
    当操作失败时抛出。
    """

    pass


class InvalidOperationError(CyanException):
    """
    当操作不合法时抛出。
    """

    pass


class InvalidTargetError(CyanException):
    """
    当目标无效时抛出。
    """

    pass


class OpenApiError(CyanException):
    """
    当 OpenAPI 返回错误时抛出。
    """

    _code: int
    _message: str
    _status_code: int

    def __init__(self, status_code: int, code: int, message: str):
        """
        初始化 `ApiError` 实例。

        参数：
            - status_code: API 状态码
            - code: HTTP 返回码
            - message: 错误消息
        """

        self._code = code
        self._message = message
        self._status_code = status_code

    @property
    def code(self):
        """
        错误代码。
        """

        return self._code

    @property
    def status_code(self):
        """
        HTTP 状态码。
        """

        return self._status_code

    @property
    def message(self):
        """
        错误消息。
        """

        return self._message
