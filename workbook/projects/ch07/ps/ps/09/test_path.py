import unittest
from unittest.mock import patch
from path import *

class TestPathCommandsAndStrategies(unittest.TestCase):
    
    @patch('builtins.print')
    def test_moveto_command(self, mock_print):
        path = Path()
        command = MovetoCommand(10, 20)
        path.execute_command(command)
        mock_print.assert_called_with("Move to: (10, 20)")

    @patch('builtins.print')
    def test_lineto_command(self, mock_print):
        path = Path()
        command = LinetoCommand(30, 40)
        path.execute_command(command)
        mock_print.assert_called_with("Draw line to: (30, 40)")

    @patch('builtins.print')
    def test_curveto_command(self, mock_print):
        path = Path()
        command = CurvetoCommand(15, 25, 20, 30, 25, 35)
        path.execute_command(command)
        mock_print.assert_called_with("Draw cubic Bézier curve: (15, 25) -> (20, 30) -> (25, 35)")

    @patch('builtins.print')
    def test_raster_draw_strategy(self, mock_print):
        path = Path(RasterDrawStrategy())
        path.draw()
        mock_print.assert_called_with("Raster drawing of path")

    @patch('builtins.print')
    def test_vector_draw_strategy(self, mock_print):
        path = Path(VectorDrawStrategy())
        path.draw()
        mock_print.assert_called_with("Vector drawing of path")

    @patch('builtins.print')
    def test_switch_draw_strategy(self, mock_print):
        path = Path(RasterDrawStrategy())
        path.draw()  # Initially use Raster strategy
        mock_print.assert_called_with("Raster drawing of path")
        
        # Change to Vector strategy
        path.set_draw_strategy(VectorDrawStrategy())
        path.draw()
        mock_print.assert_called_with("Vector drawing of path")

    @patch('builtins.print')
    def test_composite_path_moveto_command(self, mock_print):
        composite_path = CompositePath()
        path1 = Path()
        path2 = Path()
        
        composite_path.add(path1)
        composite_path.add(path2)
        
        command = MovetoCommand(10, 10)
        composite_path.execute_command(command)
        
        # Check if moveto command is executed on all paths in composite
        mock_print.assert_any_call("Move to: (10, 10)")

    @patch('builtins.print')
    def test_composite_path_with_different_commands(self, mock_print):
        composite_path = CompositePath()
        path1 = Path()
        path2 = Path()
        
        composite_path.add(path1)
        composite_path.add(path2)
        
        moveto_command = MovetoCommand(5, 5)
        lineto_command = LinetoCommand(50, 50)
        
        composite_path.execute_command(moveto_command)
        composite_path.execute_command(lineto_command)
        
        # Verify that commands are executed on all paths
        mock_print.assert_any_call("Move to: (5, 5)")
        mock_print.assert_any_call("Draw line to: (50, 50)")

    def test_path_initial_draw_strategy(self):
        path = Path()
        self.assertIsInstance(path.draw_strategy, RasterDrawStrategy)

    def test_path_set_draw_strategy(self):
        path = Path()
        vector_strategy = VectorDrawStrategy()
        path.set_draw_strategy(vector_strategy)
        self.assertEqual(path.draw_strategy, vector_strategy)

if __name__ == "__main__":
    unittest.main()
