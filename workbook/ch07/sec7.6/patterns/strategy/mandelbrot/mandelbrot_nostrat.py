import sys

def main():
    if len(sys.argv) != 8:
        print("Usage:   python3 mandelbrot_nostrat.py <xmin> <xmax> <ymin> <ymax> <maxiter> <xres> <out.ppm>")
        print("Example: python3 mandelbrot_nostrat.py 0.27085 0.27100 0.004640 0.004810 1000 1024 pic.ppm")
        sys.exit(1)

    # command-line arguments
    xmin = float(sys.argv[1])
    xmax = float(sys.argv[2])
    ymin = float(sys.argv[3])
    ymax = float(sys.argv[4])
    maxiter = int(sys.argv[5])
    xres = int(sys.argv[6])
    filename = sys.argv[7]

    # calculate derived values
    yres = int(xres * (ymax - ymin) / (xmax - xmin))
    dx = (xmax - xmin) / xres
    dy = (ymax - ymin) / yres

    # open output file
    with open(filename, "w") as f:
        # PPM header
        f.write(f"P3\n")
        f.write(f"# Mandelbrot set: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}, maxiter={maxiter}\n")
        f.write(f"{xres} {yres}\n")
        f.write(f"255\n")  # max color value

        # Mandelbrot set and write pixel data
        for j in range(yres):
            y = ymax - j * dy
            for i in range(xres):
                x = xmin + i * dx
                u, v = 0.0, 0.0
                u2, v2 = u * u, v * v
                k = 0

                # iterate point
                while k < maxiter and (u2 + v2 < 4.0):
                    v = 2 * u * v + y
                    u = u2 - v2 + x
                    u2, v2 = u * u, v * v
                    k += 1

                # map iterations to a grayscale value
                color_value = int(255 * k / maxiter) if k < maxiter else 0
                f.write(f"{color_value} {color_value} {color_value} ")

            f.write("\n")  # end-of-row

if __name__ == "__main__":
    main()
