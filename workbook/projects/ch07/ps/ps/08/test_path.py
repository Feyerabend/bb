import unittest
from unittest.mock import patch
from path import *

# In these tests, we’re using unittest.mock.patch to mock the print function.
# This allows us to capture the output and verify that the correct messages
# are printed when commands are executed. This avoids actually printing to
# the console while still verifying the behavior of the methods.

class TestPathCommands(unittest.TestCase):
    
    @patch('builtins.print')  # Mocking print to check the output
    def test_moveto_command(self, mock_print):
        path = Path()
        command = MovetoCommand(10, 20)
        
        path.execute_command(command)  # Execute the moveto command
        
        # Check if the correct print statement was called
        mock_print.assert_called_with("Move to: (10, 20)")

    @patch('builtins.print')  # Mocking print to check the output
    def test_lineto_command(self, mock_print):
        path = Path()
        command = LinetoCommand(30, 40)
        
        path.execute_command(command)  # Execute the lineto command
        
        # Check if the correct print statement was called
        mock_print.assert_called_with("Draw line to: (30, 40)")

    @patch('builtins.print')  # Mocking print to check the output
    def test_curveto_command(self, mock_print):
        path = Path()
        command = CurvetoCommand(15, 25, 20, 30, 25, 35)
        
        path.execute_command(command)  # Execute the curveto command
        
        # Check if the correct print statement was called
        mock_print.assert_called_with(
            "Draw cubic Bézier curve: (15, 25) -> (20, 30) -> (25, 35)"
        )

    def test_composite_path_execution(self):
        path1 = Path()
        path2 = Path()
        composite_path = CompositePath()
        
        # Adding simple moveto commands to both paths
        composite_path.add(path1)
        composite_path.add(path2)
        
        moveto_command = MovetoCommand(10, 20)
        
        # Execute the moveto command on the composite path
        with patch('builtins.print') as mock_print:
            composite_path.execute_command(moveto_command)
        
        # Check that the moveto command is executed on both paths
        mock_print.assert_any_call("Move to: (10, 20)")  # For path1
        mock_print.assert_any_call("Move to: (10, 20)")  # For path2

    def test_composite_path_with_multiple_commands(self):
        path1 = Path()
        path2 = Path()
        composite_path = CompositePath()
        
        # Adding paths to the composite path
        composite_path.add(path1)
        composite_path.add(path2)
        
        # Create multiple commands
        moveto_command = MovetoCommand(10, 20)
        lineto_command = LinetoCommand(30, 40)
        
        # Execute the commands on the composite path
        with patch('builtins.print') as mock_print:
            composite_path.execute_command(moveto_command)
            composite_path.execute_command(lineto_command)
        
        # Check if both commands are applied to both paths
        mock_print.assert_any_call("Move to: (10, 20)")  # For path1
        mock_print.assert_any_call("Move to: (10, 20)")  # For path2
        mock_print.assert_any_call("Draw line to: (30, 40)")  # For path1
        mock_print.assert_any_call("Draw line to: (30, 40)")  # For path2

if __name__ == "__main__":
    unittest.main()
