import sys
from abc import ABC, abstractmethod


class ColorStrategy(ABC):
    @abstractmethod
    def get_color(self, iterations: int, max_iter: int) -> tuple[int, int, int]:
        pass


class GrayscaleStrategy(ColorStrategy):
    def get_color(self, iterations: int, max_iter: int) -> tuple[int, int, int]:
        if iterations == max_iter:
            return (0, 0, 0)
        value = int(255 * iterations / max_iter)
        return (value, value, value)

class RainbowStrategy(ColorStrategy):
    def get_color(self, iterations: int, max_iter: int) -> tuple[int, int, int]:
        if iterations == max_iter:
            return (0, 0, 0)
        ratio = iterations / max_iter
        r = int(255 * (1 - ratio))
        g = int(255 * ratio)
        b = int(255 * (0.5 + ratio/2))
        return (r, g, b)

class MandelbrotGenerator:
    def __init__(self, color_strategy: ColorStrategy):
        self.color_strategy = color_strategy

    def generate(self, xmin: float, xmax: float, ymin: float, ymax: float,
                 maxiter: int, xres: int, filename: str):
        yres = int(xres * (ymax - ymin) / (xmax - xmin))
        dx = (xmax - xmin) / xres
        dy = (ymax - ymin) / yres

        with open(filename, "w") as f:
            f.write(f"P3\n# Mandelbrot set\n{xres} {yres}\n255\n")

            for j in range(yres):
                y = ymax - j * dy
                for i in range(xres):
                    x = xmin + i * dx
                    iterations = self.calculate_iterations(x, y, maxiter)
                    color = self.color_strategy.get_color(iterations, maxiter)
                    f.write(f"{color[0]} {color[1]} {color[2]} ")
                f.write("\n")

    def calculate_iterations(self, x: float, y: float, maxiter: int) -> int:
        u, v = 0.0, 0.0
        u2, v2 = u*u, v*v
        iterations = 0

        while iterations < maxiter and (u2 + v2 < 4.0):
            v = 2 * u * v + y
            u = u2 - v2 + x
            u2, v2 = u*u, v*v
            iterations += 1

        return iterations

def main():
    if len(sys.argv) != 8:
        print("Usage:   python3 mandelbrot_strat.py <xmin> <xmax> <ymin> <ymax> <maxiter> <xres> <out.ppm>")
        print("Example: python3 mandelbrot_strat.py -2.0 1.0 -1.5 1.5 1000 1024 pic.ppm")
        sys.exit(1)

    generator = MandelbrotGenerator(
        # change to switch strategies:
        RainbowStrategy()  # or GrayscaleStrategy()
    )

    # parse arguments and generate
    generator.generate(
        xmin=float(sys.argv[1]),
        xmax=float(sys.argv[2]),
        ymin=float(sys.argv[3]),
        ymax=float(sys.argv[4]),
        maxiter=int(sys.argv[5]),
        xres=int(sys.argv[6]),
        filename=sys.argv[7]
    )

if __name__ == "__main__":
    main()
