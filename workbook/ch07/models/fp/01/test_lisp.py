import unittest
from typing import Any
from lisp import (
    Token, TokenFactory, Parser, Environment, Procedure, Lisp, ErrorHandler,
    ParseError, RuntimeError, Symbol, ExpressionFactory,
    QuoteEvaluator, IfEvaluator, CondEvaluator, AndEvaluator, OrEvaluator,
    DefineEvaluator, SetEvaluator, LambdaEvaluator, LetEvaluator,
    BeginEvaluator, WhileEvaluator, AddCommand, SubtractCommand,
    MultiplyCommand, DivideCommand, ModCommand, AbsCommand,
    MaxCommand, MinCommand, EqualCommand, NotEqualCommand,
    LessCommand, GreaterCommand, LessEqualCommand, GreaterEqualCommand,
    NotCommand, ConsCommand, CarCommand, CdrCommand, ListCommand,
    AppendCommand, LengthCommand, ReverseCommand, NullCommand,
    EmptyCommand, NumberCommand, StringCommand, SymbolCommand,
    ListPredCommand, ProcedureCommand, MapCommand, FilterCommand,
    ReduceCommand, ApplyCommand, PrintCommand, DisplayCommand
)

class TestLispInterpreter(unittest.TestCase):
    def setUp(self):
        self.lisp = Lisp()
        self.env = Environment(self.lisp.global_env)  # Set global_env as parent

    def test_token_factory(self):
        # Test valid tokenization
        text = '(+ 1 2.0 "hello" true nil)'
        tokens = TokenFactory.create_tokens(text)
        expected_kinds = ['PAREN', 'SYMBOL', 'NUMBER', 'NUMBER', 'STRING', 'SYMBOL', 'SYMBOL', 'PAREN']
        expected_values = ['(', '+', '1', '2.0', '"hello"', 'true', 'nil', ')']
        self.assertEqual(len(tokens), len(expected_kinds))
        for token, kind, value in zip(tokens, expected_kinds, expected_values):
            self.assertEqual(token.kind, kind)
            self.assertEqual(token.value, value)

        # Test unterminated string
        with self.assertRaises(ParseError) as cm:
            TokenFactory.create_tokens('"unterminated')
        self.assertIn("Unterminated string", str(cm.exception))

        # Test comments and whitespace
        text = '; comment\n (+ 1 2)'
        tokens = TokenFactory.create_tokens(text)
        self.assertEqual(len(tokens), 5)  # Should ignore comment and whitespace
        self.assertEqual(tokens[0].value, '(')
        self.assertEqual(tokens[1].value, '+')

    def test_parser(self):
        tokens = TokenFactory.create_tokens('(+ 1 2.0 "hello")')
        parser = Parser(tokens)
        parsed = parser.parse()
        expected = [Symbol('+'), 1, 2.0, 'hello']
        self.assertEqual(parsed, expected)

        # Test quote parsing
        tokens = TokenFactory.create_tokens("'x")
        parser = Parser(tokens)
        parsed = parser.parse()
        self.assertEqual(parsed, ['quote', Symbol('x')])

        # Test unexpected closing parenthesis
        tokens = TokenFactory.create_tokens(')')
        parser = Parser(tokens)
        with self.assertRaises(ParseError) as cm:
            parser.parse()
        self.assertIn("Unexpected closing", str(cm.exception))

        # Test missing closing parenthesis
        tokens = TokenFactory.create_tokens('(')
        parser = Parser(tokens)
        with self.assertRaises(ParseError) as cm:
            parser.parse()
        self.assertIn("Missing closing", str(cm.exception))

    def test_environment(self):
        env = Environment()
        env.define('x', 10)
        self.assertEqual(env.get('x'), 10)
        env.set('x', 20)
        self.assertEqual(env.get('x'), 20)

        # Test undefined variable
        with self.assertRaises(RuntimeError) as cm:
            env.get('y')
        self.assertIn("Undefined variable", str(cm.exception))

        # Test setting undefined variable
        with self.assertRaises(RuntimeError) as cm:
            env.set('y', 30)
        self.assertIn("Cannot set undefined variable", str(cm.exception))

        # Test nested environment
        parent = Environment()
        parent.define('a', 1)
        child = Environment(parent)
        self.assertEqual(child.get('a'), 1)
        child.define('a', 2)
        self.assertEqual(child.get('a'), 2)
        self.assertEqual(parent.get('a'), 1)

    def test_procedure(self):
        params = ['x', 'y']
        body = [Symbol('+'), Symbol('x'), Symbol('y')]
        proc = Procedure(params, body, self.env, self.lisp)  # Use self.env
        result = proc(1, 2)
        self.assertEqual(result, 3)

        # Test wrong number of arguments
        with self.assertRaises(RuntimeError) as cm:
            proc(1)
        self.assertIn("Function expects 2 arguments, got 1", str(cm.exception))

        # Test invalid parameter types
        with self.assertRaises(RuntimeError) as cm:
            Procedure([1], body, self.env, self.lisp)
        self.assertIn("Parameter names must be strings", str(cm.exception))

    def test_expression_factory(self):
        # Test atom creation
        token = Token('NUMBER', '123', 0)
        self.assertEqual(ExpressionFactory.create_atom(token), 123)

        token = Token('NUMBER', '12.34', 0)
        self.assertEqual(ExpressionFactory.create_atom(token), 12.34)

        token = Token('STRING', '"hello\\nworld"', 0)
        self.assertEqual(ExpressionFactory.create_atom(token), 'hello\nworld')

        token = Token('SYMBOL', 'true', 0)
        self.assertEqual(ExpressionFactory.create_atom(token), True)

        token = Token('SYMBOL', 'x', 0)
        self.assertEqual(ExpressionFactory.create_atom(token), Symbol('x'))

    def test_special_forms(self):
        # Test quote
        result = self.lisp.eval([Symbol('quote'), Symbol('x')], self.env)
        self.assertEqual(result, Symbol('x'))

        # Test if
        result = self.lisp.eval([Symbol('if'), True, 1, 2], self.env)
        self.assertEqual(result, 1)
        result = self.lisp.eval([Symbol('if'), False, 1, 2], self.env)
        self.assertEqual(result, 2)

        # Test cond
        result = self.lisp.eval([Symbol('cond'), [True, 1], [Symbol('else'), 2]], self.env)
        self.assertEqual(result, 1)
        result = self.lisp.eval([Symbol('cond'), [False, 1], [Symbol('else'), 2]], self.env)
        self.assertEqual(result, 2)

        # Test and
        result = self.lisp.eval([Symbol('and'), True, True], self.env)
        self.assertEqual(result, True)
        result = self.lisp.eval([Symbol('and'), True, False], self.env)
        self.assertEqual(result, False)

        # Test or
        result = self.lisp.eval([Symbol('or'), False, True], self.env)
        self.assertEqual(result, True)
        result = self.lisp.eval([Symbol('or'), False, False], self.env)
        self.assertEqual(result, False)

        # Test define
        self.lisp.eval([Symbol('define'), Symbol('x'), 10], self.env)
        self.assertEqual(self.env.get('x'), 10)

        # Test set!
        self.lisp.eval([Symbol('define'), Symbol('y'), 5], self.env)
        self.lisp.eval([Symbol('set!'), Symbol('y'), 15], self.env)
        self.assertEqual(self.env.get('y'), 15)

        # Test lambda
        result = self.lisp.eval([[Symbol('lambda'), [Symbol('x')], [Symbol('+'), Symbol('x'), 1]], 5], self.env)
        self.assertEqual(result, 6)

        # Test let
        result = self.lisp.eval([Symbol('let'), [[Symbol('x'), 10]], [Symbol('+'), Symbol('x'), 5]], self.env)
        self.assertEqual(result, 15)

        # Test begin
        result = self.lisp.eval([Symbol('begin'), [Symbol('define'), Symbol('z'), 1], [Symbol('+'), Symbol('z'), 2]], self.env)
        self.assertEqual(result, 3)

        # Test while
        self.lisp.eval([Symbol('define'), Symbol('i'), 0], self.env)
        result = self.lisp.eval([Symbol('while'), [Symbol('<'), Symbol('i'), 3], [Symbol('set!'), Symbol('i'), [Symbol('+'), Symbol('i'), 1]]], self.env)
        self.assertEqual(self.env.get('i'), 3)

    def test_built_in_commands(self):
        # Test arithmetic
        self.assertEqual(AddCommand().execute(1, 2, 3), 6)
        self.assertEqual(SubtractCommand().execute(10, 3, 2), 5)
        self.assertEqual(MultiplyCommand().execute(2, 3, 4), 24)
        self.assertEqual(DivideCommand().execute(100, 2, 2), 25.0)
        self.assertEqual(ModCommand().execute(10, 3), 1)
        self.assertEqual(AbsCommand().execute(-5), 5)
        self.assertEqual(MaxCommand().execute(1, 5, 3), 5)
        self.assertEqual(MinCommand().execute(1, 5, 3), 1)

        # Test comparisons
        self.assertEqual(EqualCommand().execute(5, 5), True)
        self.assertEqual(NotEqualCommand().execute(5, 6), True)
        self.assertEqual(LessCommand().execute(4, 5), True)
        self.assertEqual(GreaterCommand().execute(6, 5), True)
        self.assertEqual(LessEqualCommand().execute(5, 5), True)
        self.assertEqual(GreaterEqualCommand().execute(6, 5), True)
        self.assertEqual(NotCommand().execute(False), True)

        # Test list operations
        self.assertEqual(ConsCommand().execute(1, [2, 3]), [1, 2, 3])
        self.assertEqual(CarCommand().execute([1, 2, 3]), 1)
        self.assertEqual(CdrCommand().execute([1, 2, 3]), [2, 3])
        self.assertEqual(ListCommand().execute(1, 2, 3), [1, 2, 3])
        self.assertEqual(AppendCommand().execute([1, 2], [3, 4]), [1, 2, 3, 4])
        self.assertEqual(LengthCommand().execute([1, 2, 3]), 3)
        self.assertEqual(ReverseCommand().execute([1, 2, 3]), [3, 2, 1])
        self.assertEqual(NullCommand().execute([]), True)
        self.assertEqual(EmptyCommand().execute([]), True)
        self.assertEqual(NumberCommand().execute(42), True)
        self.assertEqual(StringCommand().execute("hello"), True)
        self.assertEqual(SymbolCommand().execute(Symbol('x')), True)
        self.assertEqual(ListPredCommand().execute([1, 2]), True)

        # Test functional commands
        self.lisp.eval([Symbol('define'), Symbol('double'), [Symbol('lambda'), [Symbol('x')], [Symbol('*'), Symbol('x'), 2]]], self.env)
        double = self.env.get('double')
        self.assertEqual(MapCommand().execute(double, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(FilterCommand().execute(lambda x: x % 2 == 0, [1, 2, 3, 4]), [2, 4])
        self.assertEqual(ReduceCommand().execute(lambda x, y: x + y, [1, 2, 3, 4]), 10)
        self.assertEqual(ApplyCommand().execute(AddCommand().execute, [1, 2, 3]), 6)

    def test_lisp_integration(self):
        # Test simple arithmetic
        self.assertEqual(self.lisp.run('(+ 1 2 3)'), 6)
        self.assertEqual(self.lisp.run('(* 2 3 4)'), 24)

        # Test function definition and application
        self.lisp.run('(define square (lambda (x) (* x x)))')
        self.assertEqual(self.lisp.run('(square 5)'), 25)

        # Test conditional
        self.assertEqual(self.lisp.run('(if (> 5 3) 10 20)'), 10)

        # Test list operations
        self.assertEqual(self.lisp.run('(cons 1 (list 2 3))'), [1, 2, 3])
        self.assertEqual(self.lisp.run('(car (list 1 2 3))'), 1)
        self.assertEqual(self.lisp.run('(cdr (list 1 2 3))'), [2, 3])

        # Test error cases
        with self.assertRaises(ParseError):
            self.lisp.run('(')  # Unclosed parenthesis
        with self.assertRaises(RuntimeError):
            self.lisp.run('(undefined)')

    def test_error_handling(self):
        # Test parse error formatting
        try:
            err = ErrorHandler.parse_error("Test error", "token", 5)
            self.assertIsInstance(err, ParseError)
            self.assertIn("at position 5 near 'token'", str(err))
        except ParseError as e:
            self.fail(f"Unexpected ParseError raised: {e}")

        # Test runtime error
        try:
            err = ErrorHandler.runtime_error("Test runtime error")
            self.assertIsInstance(err, RuntimeError)
            self.assertIn("Runtime error: Test runtime error", str(err))
        except RuntimeError as e:
            self.fail(f"Unexpected RuntimeError raised: {e}")

if __name__ == '__main__':
    unittest.main()