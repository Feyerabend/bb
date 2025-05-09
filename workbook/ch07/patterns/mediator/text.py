data = {
    'A': [((0, 0), (2.5, 10)), ((2.5, 10), (5, 0)), ((1, 5), (4, 5))],
    'B': [((0, 0), (0, 10)), ((0, 10), (3, 10)), ((3, 10), (4, 9)), ((4, 9), (4, 6)), 
          ((4, 6), (3, 5)), ((3, 5), (4, 4)), ((4, 4), (4, 1)), ((4, 1), (3, 0)), 
          ((3, 0), (0, 0)), ((0, 5), (3, 5))],
    'C': [((5, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 9)), ((0, 9), (1, 10)),
          ((1, 10), (5, 10))],
    'D': [((0, 0), (0, 10)), ((0, 10), (3, 10)), ((3, 10), (4, 9)), ((4, 9), (4, 1)),
          ((4, 1), (3, 0)), ((0, 0), (3, 0))],
    'E': [((5, 0), (0, 0)), ((0, 0), (0, 10)), ((0, 10), (5, 10)), ((0, 5), (3, 5))],
    'F': [((0, 0), (0, 10)), ((0, 10), (5, 10)), ((0, 5), (3, 5))],
    'G': [((5, 7), (5, 10)), ((5, 10), (1, 10)), ((1, 10), (0, 9)), ((0, 9), (0, 1)),
          ((0, 1), (1, 0)), ((1, 0), (5, 0)), ((5, 0), (5, 4)), ((3, 4), (5, 4))],
    'H': [((0, 0), (0, 10)), ((5, 0), (5, 10)), ((0, 5), (5, 5))],
    'I': [((2, 0), (2, 10)), ((0, 0), (4, 0)), ((0, 10), (4, 10))],
    'J': [((5, 10), (5, 1)), ((5, 1), (4, 0)), ((4, 0), (1, 0)), ((1, 0), (0, 1))],
    'K': [((0, 0), (0, 10)), ((5, 10), (0, 5)), ((0, 5), (5, 0))],
    'L': [((0, 10), (0, 0)), ((0, 0), (5, 0))],
    'M': [((0, 0), (0, 10)), ((0, 10), (2.5, 5)), ((2.5, 5), (5, 10)), ((5, 10), (5, 0))],
    'N': [((0, 0), (0, 10)), ((0, 10), (5, 0)), ((5, 0), (5, 10))],
    'O': [((0, 0), (5, 0)), ((5, 0), (5, 10)), ((5, 10), (0, 10)), ((0, 10), (0, 0))],
    'P': [((0, 0), (0, 10)), ((0, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 6)),
          ((5, 6), (4, 5)), ((4, 5), (0, 5))],
    'Q': [((0, 0), (5, 0)), ((5, 0), (5, 10)), ((5, 10), (0, 10)), ((0, 10), (0, 0)),
          ((3, 3), (5, 0))],
    'R': [((0, 0), (0, 10)), ((0, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 6)),
          ((5, 6), (4, 5)), ((4, 5), (0, 5)), ((0, 5), (5, 0))],
    'S': [((5, 10), (1, 10)), ((1, 10), (0, 9)), ((0, 9), (1, 5)), ((1, 5), (4, 5)), 
          ((4, 5), (5, 1)), ((5, 1), (4, 0)), ((4, 0), (0, 0))],
    'T': [((2.5, 0), (2.5, 10)), ((0, 10), (5, 10))],
    'U': [((0, 10), (0, 1)), ((0, 1), (1, 0)), ((1, 0), (4, 0)), ((4, 0), (5, 1)),
          ((5, 1), (5, 10))],
    'V': [((0, 10), (2.5, 0)), ((2.5, 0), (5, 10))],
    'W': [((0, 10), (1.5, 0)), ((1.5, 0), (2.5, 5)), ((2.5, 5), (3.5, 0)), ((3.5, 0), (5, 10))],
    'X': [((0, 10), (5, 0)), ((5, 10), (0, 0))],
    'Y': [((0, 10), (2.5, 5)), ((2.5, 5), (5, 10)), ((2.5, 5), (2.5, 0))],
    'Z': [((0, 10), (5, 10)), ((5, 10), (0, 0)), ((0, 0), (5, 0))],
    '0': [((1, 0), (4, 0)), ((4, 0), (5, 1)), ((5, 1), (5, 9)), ((5, 9), (4, 10)),
          ((4, 10), (1, 10)), ((1, 10), (0, 9)), ((0, 9), (0, 1)), ((0, 1), (1, 0)),
          ((5, 10), (0, 0))],
    '1': [((2.5, 0), (2.5, 10))],
    '2': [((0, 9), (1, 10)), ((1, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 5)), 
          ((5, 5), (0, 0)), ((0, 0), (5, 0))],
    '3': [((0, 10), (5, 10)), ((5, 10), (3, 5)), ((3, 5), (5, 0)), ((0, 0), (5, 0))],
    '4': [((4, 10), (4, 0)), ((0, 5), (5, 5)), ((4, 10), (0, 5))],
    '5': [((5, 10), (0, 10)), ((0, 10), (0, 5)), ((0, 5), (4, 5)), ((4, 5), (5, 4)),
          ((5, 4), (5, 0)), ((5, 0), (0, 0))],
    '6': [((5, 10), (0, 10)), ((0, 10), (0, 0)), ((0, 0), (5, 0)), ((5, 0), (5, 4)), 
          ((5, 4), (4, 5)), ((4, 5), (0, 5))],
    '7': [((0, 10), (5, 10)), ((5, 10), (2, 0))],
    '8': [((1, 5), (4, 5)), ((1, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 1)), 
          ((5, 1), (4, 0)), ((4, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 9)), 
          ((0, 9), (1, 10))],
    '9': [((5, 0), (5, 10)), ((5, 10), (0, 10)), ((0, 10), (0, 6)), ((0, 6), (1, 5)), 
          ((1, 5), (5, 5))]
}

class RenderingMediator:
    def __init__(self):
        self.width = 650
        self.height = 50
        self.scale = 1.1
        self.margin = 15
        self.spacing = 8
        self.bresenham_image = [[[255, 255, 255] for _ in range(self.width)] for _ in range(self.height)]
        self.wu_image = [[[255, 255, 255] for _ in range(self.width)] for _ in range(self.height)]
        self.renderer = CharacterRenderer(self)
        self.line_drawer = LineDrawer(self)
        self.character_data_provider = CharacterDataProvider(data)
        
    def render_text(self, text):
        x = self.margin
        start_y = self.height // 2
        
        for char in text:
            char_lines = self.character_data_provider.get_character_data(char)
            if char_lines:
                self.renderer.render_character(char_lines, x, start_y)
            x += self.spacing * self.scale
            
    def save_images(self, bresenham_file, wu_file):
        self._save_image(self.bresenham_image, bresenham_file)
        self._save_image(self.wu_image, wu_file)
        
    def _save_image(self, image, filename):
        with open(filename, "w") as f:
            f.write(f"P3\n{self.width} {self.height}\n255\n")
            for row in image:
                for pixel in row:
                    f.write(f"{pixel[0]} {pixel[1]} {pixel[2]} ")
                f.write("\n")


class CharacterDataProvider:
    def __init__(self, data_dict):
        self.data = data_dict
        
    def get_character_data(self, char):
        return self.data.get(char, [])


class LineDrawer:
    def __init__(self, mediator):
        self.mediator = mediator
        
    def plot_wu(self, x, y, brightness):
        if 0 <= x < self.mediator.width and 0 <= y < self.mediator.height:
            intensity = int(255 * brightness)
            self.mediator.wu_image[y][x] = (intensity, intensity, intensity)
            
    def draw_line_bresenham(self, x1, y1, x2, y2):
        img = self.mediator.bresenham_image
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            if 0 <= x1 < len(img[0]) and 0 <= y1 < len(img):
                img[y1][x1] = (0, 0, 0)
            if (x1, y1) == (x2, y2):
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
                
    def draw_line_wu(self, x0, y0, x1, y1):
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1

        xend = round(x0)
        yend = y0 + gradient * (xend - x0)
        xgap = 1 - (x0 + 0.5 - int(x0 + 0.5))
        xpxl1 = xend
        ypxl1 = int(yend)
        
        if steep:
            self.plot_wu(ypxl1, xpxl1, (1 - (yend - ypxl1)) * xgap)
            self.plot_wu(ypxl1 + 1, xpxl1, (yend - ypxl1) * xgap)
        else:
            self.plot_wu(xpxl1, ypxl1, (1 - (yend - ypxl1)) * xgap)
            self.plot_wu(xpxl1, ypxl1 + 1, (yend - ypxl1) * xgap)

        intery = yend + gradient
        for x in range(xpxl1 + 1, int(x1)):
            y = int(intery)
            if steep:
                self.plot_wu(y, x, 1 - (intery - y))
                self.plot_wu(y + 1, x, intery - y)
            else:
                self.plot_wu(x, y, 1 - (intery - y))
                self.plot_wu(x, y + 1, intery - y)
            intery += gradient

        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = x1 + 0.5 - int(x1 + 0.5)
        xpxl2 = xend
        ypxl2 = int(yend)
        
        if steep:
            self.plot_wu(ypxl2, xpxl2, (1 - (yend - ypxl2)) * xgap)
            self.plot_wu(ypxl2 + 1, xpxl2, (yend - ypxl2) * xgap)
        else:
            self.plot_wu(xpxl2, ypxl2, (1 - (yend - ypxl2)) * xgap)
            self.plot_wu(xpxl2, ypxl2 + 1, (yend - ypxl2) * xgap)


class CharacterRenderer:
    def __init__(self, mediator):
        self.mediator = mediator
        
    def render_character(self, char_lines, x, start_y):
        for line in char_lines:
            (x1, y1), (x2, y2) = line
            
            scaled_x1 = int(x + x1 * self.mediator.scale)
            scaled_y1 = int(start_y - y1 * self.mediator.scale)
            scaled_x2 = int(x + x2 * self.mediator.scale)
            scaled_y2 = int(start_y - y2 * self.mediator.scale)
            
            self.mediator.line_drawer.draw_line_wu(scaled_x1, scaled_y1, scaled_x2, scaled_y2)
            self.mediator.line_drawer.draw_line_bresenham(scaled_x1, scaled_y1, scaled_x2, scaled_y2)


class TextRenderingFacade:
    def __init__(self):
        self.mediator = RenderingMediator()
    
    def render_text_to_files(self, text, bresenham_file, wu_file):
        self.mediator.render_text(text)
        self.mediator.save_images(bresenham_file, wu_file)


def main():
    facade = TextRenderingFacade()
    facade.render_text_to_files(
        "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG      0 1 2 3 4 5 6 7 8 9",
        "text_bresenham.ppm",
        "text_wu.ppm"
    )
    print("Text rendering complete!")

if __name__ == "__main__":
    main()
