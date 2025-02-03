class VM:
    def __init__(self):
        self.variables = {}
        self.instructions = []
        self.pc = 0
        self.labels = {}
        self.call_stack = []
        self.comparison_ops = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '!=': lambda a, b: a != b,
            '<=': lambda a, b: a <= b,
            '==': lambda a, b: a == b
        }

    def load_instruction(self, instruction):
        """Load instruction and track labels/variables"""
        if instruction.get('op') == 'LABEL':
            label = instruction.get('result')
            if label:
                self.labels[label] = len(self.instructions)
        
        # Track variables in all fields
        for field in ['arg1', 'arg2', 'result']:
            val = instruction.get(field)
            if val and not val.isdigit() and val != 'NULL':
                self.variables.setdefault(val, 0)
                
        self.instructions.append(instruction)

    def load_instructions_from_file(self, filename):
        """Load instructions from file with robust parsing"""
        try:
            with open(filename, 'r') as file:
                current = {}
                for line in file:
                    line = line.strip()
                    if not line:
                        if current:
                            self.load_instruction(current)
                            current = {}
                        continue
                    
                    # Handle all possible fields
                    if line.startswith('TYPE:'):
                        current['op'] = line.split('TYPE: ')[1]
                    elif line.startswith('ARG1:'):
                        current['arg1'] = line.split('ARG1: ')[1]
                    elif line.startswith('ARG2:'):
                        current['arg2'] = line.split('ARG2: ')[1]
                    elif line.startswith('RESULT:'):
                        current['result'] = line.split('RESULT: ')[1]
                
                if current:
                    self.load_instruction(current)
                    
        except Exception as e:
            print(f"Load error: {str(e)}")
            raise

    def get_val(self, arg):
        """Get value from variable or literal"""
        if arg == 'NULL': return None
        if arg.isdigit(): return int(arg)
        return self.variables.get(arg, 0)

    def execute(self):
        """Execute loaded program with full feature support"""
        print("Starting execution...")
        self.pc = 0

        # search for main label and start execution at that point
        if 'main' in self.labels:
            self.pc = self.labels['main']
        else:
            print("No main label found")

        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            op = instr['op']
            arg1 = instr.get('arg1', 'NULL')
            arg2 = instr.get('arg2', 'NULL')
            result = instr.get('result', 'NULL')
            
            try:
                # Handle control flow first
                if op == 'LABEL':
                    self.pc += 1
                    continue
                    
                elif op == 'GOTO':
                    self.pc = self.labels[arg1]
                    continue
                    
                elif op == 'IF_NOT':
                    if not self.get_val(arg1):
                        self.pc = self.labels[arg2]
                    else:
                        self.pc += 1
                    continue
                    
                elif op == 'CALL':
                    self.call_stack.append(self.pc + 1)
                    self.pc = self.labels[arg1]
                    continue
                    
                elif op == 'RETURN':
                    self.pc = self.call_stack.pop()
                    continue

                # Handle assignments and operations
                val1 = self.get_val(arg1)
                val2 = self.get_val(arg2) if arg2 != 'NULL' else None

                if op == '=':
                    self.variables[result] = val1
                    
                elif op in self.comparison_ops:
                    cmp_result = self.comparison_ops[op](val1, val2)
                    self.variables[result] = 1 if cmp_result else 0
                    
                elif op == '+':
                    self.variables[result] = val1 + val2
                    
                elif op == '-':
                    self.variables[result] = val1 - val2
                    
                elif op == '*':
                    self.variables[result] = val1 * val2
                    
                elif op == '/':
                    self.variables[result] = val1 // val2
                    
                elif op == 'LOAD':
                    self.variables[result] = val1
                    
                else:
                    raise RuntimeError(f"Unknown operation: {op}")

                self.pc += 1
                print(f"[{self.pc}] {op} {arg1} {arg2} -> {result}")

            except Exception as e:
                print(f"CRASH at PC {self.pc} ({instr})")
                print(f"Variables: {self.variables}")
                print(f"Call stack: {self.call_stack}")
                print(f"Labels: {self.labels}")
                print(f"Error: {str(e)}")
                return


# Horrible ... but it works
        print("Execution completed successfully")
        vars = {var: value for var, value in self.variables.items() if not (var.startswith('t') and var[1:].isdigit())}
        print(f"Variables: {vars}")
        print(f"Labels: {self.labels}")

        # Usage example
        print("---------------\n")
        filtered_variables = {var: value for var, value in vars.items() if var not in self.labels or not var.startswith('L')}
        print(filtered_variables)

# Usage example
vm = VM()
vm.load_instructions_from_file("sample2.txt")
vm.execute()