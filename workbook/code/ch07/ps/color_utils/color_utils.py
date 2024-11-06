class ColorUtils:
    @staticmethod
    def rgb_to_gray(r: int, g: int, b: int) -> int:
        return int(0.299 * r + 0.587 * g + 0.114 * b)

    @staticmethod
    def blend_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        return r, g, b
