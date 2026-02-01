from ast_nodes import *

class PicoCodeGenerator:
    """
    Code generator that produces C code for Raspberry Pi Pico 2.
    - Uses the display library for output instead of console I/O
    - Ignores 'input' statements (no input capability on embedded display)
    - Generates standalone C file that can be compiled for Pico 2
    """
    
    def __init__(self, ast):
        self.ast = ast
        self.code_lines = []
        self.indent_level = 0
        self.label_counter = 0
        self.temp_var_counter = 0
        self.display_y = 0  # Track Y position for text output
        self.variable_types = {}  # Track variable types (string or number)
        
    def generate(self):
        """Generate complete C program"""
        self.emit_header()
        self.emit_globals()
        self.emit_main_start()
        self.visit(self.ast)
        self.emit_main_end()
        return '\n'.join(self.code_lines)
    
    def emit(self, line):
        """Emit a line of code with proper indentation"""
        indent = '    ' * self.indent_level
        self.code_lines.append(indent + line)
    
    def emit_blank(self):
        """Emit a blank line"""
        self.code_lines.append('')
    
    def new_label(self):
        """Generate a unique label name"""
        label = f"label_{self.label_counter}"
        self.label_counter += 1
        return label
    
    def new_temp(self):
        """Generate a unique temporary variable name"""
        temp = f"temp_{self.temp_var_counter}"
        self.temp_var_counter += 1
        return temp
    
    def emit_header(self):
        """Emit necessary includes and defines"""
        self.emit("// Auto-generated code for Raspberry Pi Pico 2")
        self.emit("// Compiled from custom language")
        self.emit_blank()
        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <string.h>")
        self.emit("#include <math.h>")
        self.emit('#include "pico/stdlib.h"')
        self.emit('#include "display.h"')
        self.emit_blank()
        self.emit("// Display configuration")
        self.emit("#define TEXT_LINE_HEIGHT 10")
        self.emit("#define TEXT_START_X 5")
        self.emit("#define TEXT_START_Y 5")
        self.emit_blank()
    
    def emit_globals(self):
        """Emit global variable declarations"""
        self.emit("// Global variables")
        self.emit("static uint16_t display_y = TEXT_START_Y;")
        self.emit("static char print_buffer[256];")
        self.emit_blank()
        self.emit("// Helper function to print to display")
        self.emit("void display_print(const char *str) {")
        self.indent_level += 1
        self.emit("if (display_y >= DISPLAY_HEIGHT - TEXT_LINE_HEIGHT) {")
        self.indent_level += 1
        self.emit("// Screen full, clear and restart")
        self.emit("disp_clear(COLOR_BLACK);")
        self.emit("display_y = TEXT_START_Y;")
        self.indent_level -= 1
        self.emit("}")
        self.emit("disp_draw_text(TEXT_START_X, display_y, str, COLOR_WHITE, COLOR_BLACK);")
        self.emit("display_y += TEXT_LINE_HEIGHT;")
        self.indent_level -= 1
        self.emit("}")
        self.emit_blank()
        self.emit("void display_print_number(double num) {")
        self.indent_level += 1
        self.emit("if (num == (int)num) {")
        self.indent_level += 1
        self.emit("snprintf(print_buffer, sizeof(print_buffer), \"%d\", (int)num);")
        self.indent_level -= 1
        self.emit("} else {")
        self.indent_level += 1
        self.emit("snprintf(print_buffer, sizeof(print_buffer), \"%.2f\", num);")
        self.indent_level -= 1
        self.emit("}")
        self.emit("display_print(print_buffer);")
        self.indent_level -= 1
        self.emit("}")
        self.emit_blank()
    
    def emit_main_start(self):
        """Emit start of main function"""
        self.emit("int main() {")
        self.indent_level += 1
        self.emit("// Initialize stdio and display")
        self.emit("stdio_init_all();")
        self.emit_blank()
        self.emit("disp_config_t config = disp_get_default_config();")
        self.emit("if (disp_init(&config) != DISP_OK) {")
        self.indent_level += 1
        self.emit("return -1;")
        self.indent_level -= 1
        self.emit("}")
        self.emit_blank()
        self.emit("disp_clear(COLOR_BLACK);")
        self.emit("disp_set_backlight(true);")
        self.emit_blank()
        self.emit("// User program variables")
    
    def emit_main_end(self):
        """Emit end of main function"""
        self.emit_blank()
        self.emit("// Program complete - infinite loop")
        self.emit("while (1) {")
        self.indent_level += 1
        self.emit("tight_loop_contents();")
        self.indent_level -= 1
        self.emit("}")
        self.emit_blank()
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")
    
    def visit(self, node):
        """Visit a node using the visitor pattern"""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")
    
    def visit_Program(self, node):
        """Visit program node"""
        for statement in node.statements:
            self.visit(statement)
    
    def visit_LetStatement(self, node):
        """Visit let statement - declare and initialize variable"""
        expr_result = self.visit(node.expression)
        
        # Determine type based on expression
        if isinstance(node.expression, StringLiteral):
            self.variable_types[node.identifier] = 'string'
            self.emit(f"char {node.identifier}[256];")
            self.emit(f"strcpy({node.identifier}, {expr_result});")
        else:
            self.variable_types[node.identifier] = 'number'
            self.emit(f"double {node.identifier} = {expr_result};")
    
    def visit_AssignStatement(self, node):
        """Visit assignment statement"""
        expr_result = self.visit(node.expression)
        
        # For strings, use strcpy
        if isinstance(node.expression, StringLiteral):
            self.emit(f"strcpy({node.identifier}, {expr_result});")
        else:
            self.emit(f"{node.identifier} = {expr_result};")
    
    def visit_PrintStatement(self, node):
        """Visit print statement - output to display"""
        expr_result = self.visit(node.expression)
        
        # Check if it's a string literal - print directly
        if isinstance(node.expression, StringLiteral):
            self.emit(f"display_print({expr_result});")
        # Check if it's an identifier - look up type
        elif isinstance(node.expression, Identifier):
            var_type = self.variable_types.get(node.expression.name, 'number')
            if var_type == 'string':
                self.emit(f"display_print({expr_result});")
            else:
                self.emit(f"display_print_number({expr_result});")
        # Everything else is treated as a number
        else:
            self.emit(f"display_print_number({expr_result});")
    
    def visit_InputStatement(self, node):
        """Visit input statement - IGNORED on embedded system"""
        self.emit(f"// INPUT ignored on embedded system: {node.identifier}")
        self.emit(f"// Initializing {node.identifier} to 0")
        self.emit(f"{node.identifier} = 0;")
    
    def visit_IfStatement(self, node):
        """Visit if statement"""
        condition = self.visit(node.condition)
        
        self.emit(f"if ({condition}) {{")
        self.indent_level += 1
        self.visit(node.then_block)
        self.indent_level -= 1
        
        if node.else_block:
            self.emit("} else {")
            self.indent_level += 1
            self.visit(node.else_block)
            self.indent_level -= 1
        
        self.emit("}")
    
    def visit_WhileStatement(self, node):
        """Visit while statement"""
        condition = self.visit(node.condition)
        
        self.emit(f"while ({condition}) {{")
        self.indent_level += 1
        self.visit(node.body)
        self.indent_level -= 1
        self.emit("}")
    
    def visit_Block(self, node):
        """Visit block of statements"""
        for statement in node.statements:
            self.visit(statement)
    
    def visit_BinaryOp(self, node):
        """Visit binary operation"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op_map = {
            "PLUS": "+",
            "MINUS": "-",
            "TIMES": "*",
            "DIVIDE": "/",
            "MOD": "%",
            "EQ": "==",
            "NE": "!=",
            "LT": "<",
            "GT": ">",
            "LE": "<=",
            "GE": ">="
        }
        
        c_op = op_map.get(node.op)
        if c_op is None:
            raise Exception(f"Unknown operator: {node.op}")
        
        return f"({left} {c_op} {right})"
    
    def visit_UnaryOp(self, node):
        """Visit unary operation"""
        operand = self.visit(node.operand)
        
        if node.op == "MINUS":
            return f"(-{operand})"
        elif node.op == "PLUS":
            return f"(+{operand})"
        else:
            raise Exception(f"Unknown unary operator: {node.op}")
    
    def visit_NumberLiteral(self, node):
        """Visit number literal"""
        return str(node.value)
    
    def visit_StringLiteral(self, node):
        """Visit string literal"""
        # Escape special characters
        escaped = node.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{escaped}"'
    
    def visit_Identifier(self, node):
        """Visit identifier"""
        return node.name


def generate_pico_code(ast):
    """Convenience function to generate Pico C code from AST"""
    generator = PicoCodeGenerator(ast)
    return generator.generate()


if __name__ == "__main__":
    from lexer import tokenize
    from parser import Parser
    
    # Test with a simple program
    code = '''
let x = 10;
let y = 20;
print("Starting program...");
if x < y {
    print("x is smaller than y");
    let z = x + y;
    print(z);
}
let i = 0;
while i < 5 {
    print(i);
    i = i + 1;
}
print("Done!");
'''
    
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    generator = PicoCodeGenerator(ast)
    c_code = generator.generate()
    
    print("=== Generated C code for Raspberry Pi Pico 2 ===")
    print(c_code)
