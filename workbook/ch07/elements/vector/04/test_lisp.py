import unittest
from unittest.mock import patch, MagicMock
from lisp import Lisp, SyntaxError, RuntimeError, GraphicsContext

class TestLispInterpreter(unittest.TestCase):
    def setUp(self):
        self.lisp = Lisp()

    def test_tokenize(self):
        program = '(+ 1 2)'
        tokens = self.lisp.tokenize(program)
        self.assertEqual(tokens, ['(', '+', '1', '2', ')'])

        program = '(define x "hello")'
        tokens = self.lisp.tokenize(program)
        self.assertEqual(tokens, ['(', 'define', 'x', '"hello"', ')'])

        program = "'(1 2 3)"
        tokens = self.lisp.tokenize(program)
        self.assertEqual(tokens, ['(', 'quote', '(', '1', '2', '3', ')', ')'])

    def test_parse(self):
        program = '(+ 1 2)'
        parsed = self.lisp.parse(program)
        self.assertEqual(parsed, ['+', 1, 2])

        program = '(define (square x) (* x x))'
        parsed = self.lisp.parse(program)
        self.assertEqual(parsed, ['define', ['square', 'x'], ['*', 'x', 'x']])

        with self.assertRaises(SyntaxError):
            self.lisp.parse('(define x 1')

    def test_arithmetic(self):
        self.assertEqual(self.lisp.run('(+ 1 2)'), 3)
        self.assertEqual(self.lisp.run('(- 5 3)'), 2)
        self.assertEqual(self.lisp.run('(* 4 2)'), 8)
        self.assertEqual(self.lisp.run('(/ 10 2)'), 5.0)
        self.assertEqual(self.lisp.run('(expt 2 3)'), 8)

    def test_special_forms(self):
        # Test if
        self.assertEqual(self.lisp.run('(if true 1 2)'), 1)
        self.assertEqual(self.lisp.run('(if false 1 2)'), 2)

        # Test define and lambda
        self.lisp.run('(define (square x) (* x x))')
        self.assertEqual(self.lisp.run('(square 4)'), 16)

        # Test let
        program = '(let ((x 2) (y 3)) (+ x y))'
        self.assertEqual(self.lisp.run(program), 5)

    def test_list_operations(self):
        self.assertEqual(self.lisp.run('(cons 1 (list 2 3))'), [1, 2, 3])
        self.assertEqual(self.lisp.run('(car (list 1 2 3))'), 1)
        self.assertEqual(self.lisp.run('(cdr (list 1 2 3))'), [2, 3])
        self.assertEqual(self.lisp.run('(length (list 1 2 3))'), 3)
        self.assertEqual(self.lisp.run('(null? (list))'), True)

    @patch('lisp.GraphicsContext')
    def test_graphics_commands(self, mock_graphics_context):
        mock_instance = mock_graphics_context.return_value
        mock_instance.commands = {
            'draw-circle': MagicMock(),
            'set-color': MagicMock(),
            'save': MagicMock()
        }

        self.lisp.run('(set-color 255 0 0)')
        mock_instance.commands['set-color'].assert_called_with(255, 0, 0, 255)

        self.lisp.run('(draw-circle 100 100 50)')
        mock_instance.commands['draw-circle'].assert_called_with(100, 100, 50)

        self.lisp.run('(save "test.png")')
        mock_instance.commands['save'].assert_called_with("test.png")

    def test_error_handling(self):
        with self.assertRaises(SyntaxError):
            self.lisp.run('(if 1 2)')  # Missing else clause

        with self.assertRaises(RuntimeError):
            self.lisp.run('(undefined-variable)')  # Undefined variable

        with self.assertRaises(SyntaxError):
            self.lisp.run('(define)')  # Invalid define syntax

    def test_string_operations(self):
        self.assertEqual(self.lisp.run('(string-append "hello" "world")'), '"helloworld"')
        self.assertEqual(self.lisp.run('(string-length "hello")'), 5)
        self.assertEqual(self.lisp.run('(substring "hello" 1 3)'), '"el"')

    def test_control_flow(self):
        program = '''
        (begin
          (define x 0)
          (while (< x 3)
            (set! x (+ x 1)))
          x)
        '''
        self.assertEqual(self.lisp.run(program), 3)

if __name__ == '__main__':
    unittest.main()