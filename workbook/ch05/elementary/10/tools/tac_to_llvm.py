from llvmlite import ir
import re

class TACToLLVMConverter:
    def __init__(self):
        self.module = ir.Module(name="main")
        self.builder = None
        self.variables = {}
        self._init_module()

    def _init_module(self):
        # Create main function
        func_type = ir.FunctionType(ir.IntType(32), [])
        func = ir.Function(self.module, func_type, name="main")
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

    def _get_or_create_var(self, name):
        if name not in self.variables:
            # Create new allocation for variable
            var = self.builder.alloca(ir.IntType(32), name=name)
            self.variables[name] = var
        return self.variables[name]

    def _parse_value(self, value):
        try:
            return ir.Constant(ir.IntType(32), int(value))
        except ValueError:
            var = self.variables.get(value)
            if var is None:
                raise ValueError(f"Undefined variable: {value}")
            return self.builder.load(var)

    def convert_instruction(self, tac_line):
        try:
            # Skip empty lines and comments
            if not tac_line.strip() or tac_line.strip().startswith('#'):
                return

            # Parse assignment
            match = re.match(r'(\w+)\s*=\s*(.+)', tac_line)
            if not match:
                raise ValueError(f"Invalid TAC instruction: {tac_line}")

            target, expression = match.groups()
            
            # Handle LOAD
            if 'LOAD' in expression:
                value = expression.split()[-1]
                var = self._get_or_create_var(target)
                self.builder.store(self._parse_value(value), var)
                
            # Handle operations
            elif any(op in expression for op in ['+', '-', '*', '/']):
                parts = expression.split()
                op = parts[0]
                operands = [self._parse_value(x) for x in parts[1:]]
                
                result = None
                if op == '+':
                    result = self.builder.add(operands[0], operands[1])
                elif op == '-':
                    result = self.builder.sub(operands[0], operands[1])
                elif op == '*':
                    result = self.builder.mul(operands[0], operands[1])
                elif op == '/':
                    result = self.builder.sdiv(operands[0], operands[1])
                
                var = self._get_or_create_var(target)
                self.builder.store(result, var)

            else:
                # Simple assignment
                var = self._get_or_create_var(target)
                value = self._parse_value(expression)
                self.builder.store(value, var)

        except Exception as e:
            raise ValueError(f"Error processing line '{tac_line}': {str(e)}")

    def convert(self, tac_code):
        for line in tac_code:
            self.convert_instruction(line.strip())
        
        # Add return 0 at the end of main
        self.builder.ret(ir.Constant(ir.IntType(32), 0))
        return str(self.module)