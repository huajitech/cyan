class ARGB:
    """
    ARGB 色彩值。
    """

    _alpha: int
    _red: int
    _green: int
    _blue: int

    @property
    def alpha(self) -> int:
        """
        Alpha 透明度通道。
        """

        return self._alpha

    @property
    def red(self) -> int:
        """
        红色通道。
        """

        return self._red

    @property
    def green(self) -> int:
        """
        绿色通道。
        """

        return self._green

    @property
    def blue(self) -> int:
        """
        蓝色通道。
        """

        return self._blue

    def __init__(self, alpha: int, red: int, green: int, blue: int) -> None:
        """
        初始化 `ARGB` 实例。

        参数：
            - alpha: Alpha 透明度通道（值范围：0-255）
            - red: 红色通道（值范围：0-255）
            - green: 绿色通道（值范围：0-255）
            - blue: 蓝色通道（值范围：0-255）
        """

        if not (0 <= alpha < 256 and 0 <= red < 256 and 0 <= green < 256 and 0 <= blue < 256):
            raise ValueError("值超出范围。")

        self._alpha = alpha
        self._red = red
        self._green = green
        self._blue = blue

    def to_hex(self) -> int:
        """
        转换 `ARGB` 为 HEX 颜色值。

        返回：
            以 `int` 形式表达的 HEX 颜色值。
        """

        return (self.alpha << 24) + (self.red << 16) + (self.green << 8) + self.blue

    @staticmethod
    def from_hex(number: int) -> "ARGB":
        """
        转换 `ARGB` HEX 颜色值的 `int` 形式为 `ARGB`。

        参数：
            - number: 以 `int` 形式表达的 HEX 颜色值

        返回：
            `ARGB` 类型表示的 ARGB 颜色值。
        """

        alpha = (number & 0xFF000000) >> 24
        red = (number & 0x00FF0000) >> 16
        green = (number & 0x0000FF00) >> 8
        blue = number & 0x000000FF
        return ARGB(alpha, red, green, blue)

    def __str__(self) -> str:
        return f"({self.alpha}, {self.red}, {self.green}, {self.blue})"
