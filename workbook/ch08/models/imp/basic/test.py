import unittest
from unittest.mock import patch
from basic import (
    InterpreterState, ExpressionParser, EvaluationVisitor, 
    NumberExpression, StringExpression, VariableExpression, 
    BinaryExpression, FunctionExpression,
    PrintCommand, LetCommand, InputCommand, IfCommand,
    GotoCommand, GosubCommand, ReturnCommand,
    ForCommand, NextCommand, WhileCommand, WendCommand
)

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        # Reset the singleton state before each test
        InterpreterState._instance = None
        self.state = InterpreterState()
        self.evaluator = EvaluationVisitor()

    def test_number_expression(self):
        expr = NumberExpression(42)
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 42)

    def test_string_expression(self):
        expr = StringExpression("Hello")
        result = expr.accept(self.evaluator)
        self.assertEqual(result, "Hello")

    def test_variable_expression(self):
        self.state.variables["X"] = 100
        expr = VariableExpression("X")
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 100)

    def test_variable_expression_unset(self):
        expr = VariableExpression("Y")
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 0)  # Default numeric variable
        expr = VariableExpression("Y$")
        result = expr.accept(self.evaluator)
        self.assertEqual(result, "")  # Default string variable

    def test_binary_expression_addition(self):
        expr = BinaryExpression(
            NumberExpression(5), "+", NumberExpression(3)
        )
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 8)

    def test_binary_expression_string_concat(self):
        expr = BinaryExpression(
            StringExpression("Hello"), "+", StringExpression("World")
        )
        result = expr.accept(self.evaluator)
        self.assertEqual(result, "HelloWorld")

    def test_function_expression_len(self):
        expr = FunctionExpression("LEN", [StringExpression("Test")])
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 4)

    def test_function_expression_sqrt(self):
        expr = FunctionExpression("SQR", [NumberExpression(16)])
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 4.0)

    def test_parser_number(self):
        parser = ExpressionParser("123.45")
        expr = parser.parse()
        result = expr.accept(self.evaluator)
        self.assertAlmostEqual(result, 123.45)

    def test_parser_string(self):
        parser = ExpressionParser('"Hello World"')
        expr = parser.parse()
        result = expr.accept(self.evaluator)
        self.assertEqual(result, "Hello World")

    def test_parser_binary(self):
        parser = ExpressionParser("2 + 3 * 4")
        expr = parser.parse()
        result = expr.accept(self.evaluator)
        self.assertEqual(result, 14)  # Should now handle precedence correctly

    def test_print_command(self):
        cmd = PrintCommand()
        self.state.variables["X"] = 42
        with patch('builtins.print') as mocked_print:
            cmd.execute("X; ' plus '; 8")
            mocked_print.assert_called_with("42 plus 8")

    def test_let_command(self):
        cmd = LetCommand()
        cmd.execute("X = 42 + 8")
        self.assertEqual(self.state.variables["X"], 50)

    def test_input_command(self):
        cmd = InputCommand()
        with patch('builtins.input', return_value="123"):
            cmd.execute('"Enter number"; X')
            self.assertEqual(self.state.variables["X"], 123)

    def test_if_command_goto(self):
        cmd = IfCommand()
        self.state.code[100] = "PRINT 'Test'"
        cmd.execute("1 = 1 THEN 100")
        self.assertEqual(self.state.variables["#"], 100)

    def test_goto_command(self):
        cmd = GotoCommand()
        self.state.code[200] = "PRINT 'Test'"
        cmd.execute("200")
        self.assertEqual(self.state.variables["#"], 200)

    def test_gosub_return(self):
        gosub = GosubCommand()
        ret = ReturnCommand()
        self.state.code[300] = "RETURN"
        self.state.variables["#"] = 10
        gosub.execute("300")
        self.assertEqual(self.state.stack, [11])
        ret.execute("")
        self.assertEqual(self.state.variables["#"], 11)
        self.assertEqual(self.state.stack, [])

    def test_for_next(self):
        for_cmd = ForCommand()
        next_cmd = NextCommand()
        self.state.variables["#"] = 10
        self.state.code[10] = "FOR I = 1 TO 3"
        for_cmd.execute("I = 1 TO 3 STEP 1")
        self.assertEqual(self.state.variables["I"], 1)
        self.assertEqual(self.state.loops["I"], (10, 3, 1))
        next_cmd.execute("I")
        self.assertEqual(self.state.variables["I"], 2)
        self.assertEqual(self.state.variables["#"], 11)

    def test_while_wend(self):
        while_cmd = WhileCommand()
        wend_cmd = WendCommand()
        self.state.variables["#"] = 20
        self.state.variables["X"] = 1
        while_cmd.execute("X < 3")
        loop_id = f"while_20"
        self.assertIn(loop_id, self.state.whiles)
        self.assertEqual(self.state.whiles[loop_id], (20, "X < 3"))
        self.state.variables["X"] = 2
        wend_cmd.execute("")
        self.assertEqual(self.state.variables["#"], 21)

if __name__ == '__main__':
    unittest.main()