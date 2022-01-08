class ARGB:
    """
    ARGB 色彩值。
    """

    _alpha: int
    _red: int
    _green: int
    _blue: int

    @property
    def alpha(self):
        """
        Alpha 透明度通道。
        """

        return self._alpha

    @property
    def red(self):
        """
        红色通道。
        """

        return self._red

    @property
    def green(self):
        """
        绿色通道。
        """

        return self._green

    @property
    def blue(self):
        """
        蓝色通道。
        """

        return self._blue

    def __init__(self, alpha: int, red: int, green: int, blue: int):
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

    def to_hex(self):
        """
        转化 `ARGB` 为 HEX 颜色值的 `int` 形式。
        """

        return (self.alpha << 24) + (self.red << 16) + (self.green << 8) + self.blue

    @staticmethod
    def from_hex(number: int):
        """
        转化 `ARGB` HEX 颜色值的 `int` 形式为 `ARGB`。
        """

        alpha = (number & 0xFF000000) >> 24
        red = (number & 0x00FF0000) >> 16
        green = (number & 0x0000FF00) >> 8
        blue = number & 0x000000FF
        return ARGB(alpha, red, green, blue)

    def __str__(self):
        return f"({self.alpha}, {self.red}, {self.green}, {self.blue})"
