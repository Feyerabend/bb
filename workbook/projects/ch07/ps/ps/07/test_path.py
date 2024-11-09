import unittest
from path import Path

class TestPath(unittest.TestCase):
    def test_moveto(self):
        path = Path()
        path.moveto(10, 20)
        commands = path.get_path_data()
        self.assertEqual(commands, [('moveto', 10, 20)])

    def test_lineto(self):
        path = Path()
        path.moveto(10, 20)  # Start at (10, 20)
        path.lineto(30, 40)
        commands = path.get_path_data()
        self.assertEqual(commands, [('moveto', 10, 20), ('lineto', 30, 40)])

    def test_curveto(self):
        path = Path()
        path.moveto(10, 20)
        path.curveto(15, 25, 20, 30, 25, 35)
        commands = path.get_path_data()
        self.assertEqual(commands, [('moveto', 10, 20), ('curveto', 15, 25, 20, 30, 25, 35)])

    def test_closepath(self):
        path = Path()
        path.moveto(10, 20)
        path.lineto(30, 40)
        path.closepath()
        commands = path.get_path_data()
        self.assertEqual(commands, [('moveto', 10, 20), ('lineto', 30, 40), ('closepath',)])

    def test_draw(self):
        path = Path()
        path.moveto(10, 20)
        path.lineto(30, 40)
        path.curveto(15, 25, 20, 30, 25, 35)
        path.closepath()
        expected_output = (
            "Move to: (10, 20)\n"
            "Draw line to: (30, 40)\n"
            "Draw cubic Bézier curve with control points: (15, 25) -> (20, 30) -> (25, 35)\n"
            "Close path\n"
        )
        self.assertEqual(path.draw(), expected_output)

    def test_empty_path(self):
        path = Path()
        self.assertEqual(path.draw(), "")

if __name__ == "__main__":
    unittest.main()
