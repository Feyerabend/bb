# test_parser.py
import unittest

from lexer import Lexer
from parser import Parser, ASTNode


class TestPostScriptParser(unittest.TestCase):

    def parse_code(self, code: str) -> ASTNode:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_single_number_push(self):
        code = "123"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "Push")
        self.assertEqual(ast.children[0].value, 123)

    def test_single_string_push(self):
        code = "(hello)"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "Push")
        self.assertEqual(ast.children[0].value, "hello")

    def test_single_name_push(self):
        code = "/name"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "Push")
        self.assertEqual(ast.children[0].value, "/name")

    def test_operator_add(self):
        code = "add"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "Operator")
        self.assertEqual(ast.children[0].value, "add")

    def test_moveto_path_command(self):
        code = "moveto 10 20"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "PathCommand")
        self.assertEqual(ast.children[0].value, "moveto")
        self.assertEqual(len(ast.children[0].children), 2)
        self.assertEqual(ast.children[0].children[0].value, 10)
        self.assertEqual(ast.children[0].children[1].value, 20)

    def test_curveto_path_command(self):
        code = "curveto 10 20 30 40 50 60"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "PathCommand")
        self.assertEqual(ast.children[0].value, "curveto")
        self.assertEqual(len(ast.children[0].children), 6)
        self.assertEqual(ast.children[0].children[0].value, 10)
        self.assertEqual(ast.children[0].children[1].value, 20)
        self.assertEqual(ast.children[0].children[2].value, 30)
        self.assertEqual(ast.children[0].children[3].value, 40)
        self.assertEqual(ast.children[0].children[4].value, 50)
        self.assertEqual(ast.children[0].children[5].value, 60)

    def test_setcolor_graphics_state_command(self):
        code = "setcolor 1 0 0"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "GraphicsStateCommand")
        self.assertEqual(ast.children[0].value, "setcolor")
        self.assertEqual(len(ast.children[0].children), 3)
        self.assertEqual(ast.children[0].children[0].value, 1)
        self.assertEqual(ast.children[0].children[1].value, 0)
        self.assertEqual(ast.children[0].children[2].value, 0)

    def test_dict_dictionary_command(self):
        code = "dict 10"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "DictionaryCommand")
        self.assertEqual(ast.children[0].value, "dict")
        self.assertEqual(len(ast.children[0].children), 1)
        self.assertEqual(ast.children[0].children[0].value, 10)

    def test_repeat_control_structure(self):
        code = "repeat 3 { moveto 10 10 lineto 20 20 }"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "ControlStructure")
        self.assertEqual(ast.children[0].value, "repeat")
        self.assertEqual(ast.children[0].children[0].value, 3)
        self.assertEqual(ast.children[0].children[1].type, "Block")
        self.assertEqual(len(ast.children[0].children[1].children), 2)

    def test_ifelse_control_structure(self):
        code = "ifelse { moveto 10 10 } { lineto 20 20 }"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "ControlStructure")
        self.assertEqual(ast.children[0].value, "ifelse")
        self.assertEqual(len(ast.children[0].children), 2)
        self.assertEqual(ast.children[0].children[0].type, "Block")
        self.assertEqual(ast.children[0].children[1].type, "Block")

    def test_block(self):
        code = "{ moveto 10 20 lineto 30 40 }"
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].type, "Block")
        self.assertEqual(len(ast.children[0].children), 2)

    def test_complex_program(self):
        code = """
        /x 10 def
        moveto 100 100
        lineto 200 200
        ifelse { setcolor 0 1 0 } { setcolor 1 0 0 }
        """
        ast = self.parse_code(code)
        self.assertEqual(ast.type, "Program")
        self.assertEqual(len(ast.children), 6)
        self.assertEqual(ast.children[0].type, "Push")
        self.assertEqual(ast.children[0].value, "/x")

        self.assertEqual(ast.children[1].type, "Push")
        self.assertEqual(ast.children[1].value, 10)
#       self.assertEqual(len(ast.children[1].children), 2)

        self.assertEqual(ast.children[2].type, "Operator")
        self.assertEqual(ast.children[2].value, "def")
#       self.assertEqual(len(ast.children[2].children), 2)

        self.assertEqual(ast.children[3].type, "PathCommand")
        self.assertEqual(ast.children[3].value, "moveto")
        self.assertEqual(len(ast.children[3].children), 2)
        self.assertEqual(ast.children[4].type, "PathCommand")
        self.assertEqual(ast.children[4].value, "lineto")
        self.assertEqual(len(ast.children[4].children), 2)

        self.assertEqual(ast.children[5].type, "ControlStructure")
        self.assertEqual(ast.children[5].value, "ifelse")
        self.assertEqual(len(ast.children[5].children), 2)

#       print(ast)

if __name__ == "__main__":
    unittest.main()