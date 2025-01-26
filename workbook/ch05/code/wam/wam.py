class WAM:
    def __init__(self):
        self.registers = {
            'IP': 0,    # instruction pointer
            'CP': 0,    # current predicate
            'HP': 0,    # heap pointer
        }
        self.heap = []          # term storage
        self.stack = []         # execution stack
        self.call_stack = []    # procedure return addresses
        self.choice_points = [] # backtrack points
        self.instructions = []  # loaded program
        self.predicates = {}    # predicate table
        self.constants = {}     # constant table
        self.variables = {}     # variable table

    def load(self, compiler):
        self.instructions = compiler.instructions
        self.predicates = compiler.predicates
        self.constants = {v:k for k,v in compiler.constants.items()}
        self.variables = compiler.vars
        self.heap = [None] * (len(compiler.vars) + len(compiler.constants) + 10)  # +10 buffer

    def fetch_execute(self):
        try:
            while self.registers['IP'] < len(self.instructions):
                instr = self.instructions[self.registers['IP']]
                op, arg1, arg2 = instr
                current_ip = self.registers['IP']
                self.registers['IP'] += 1
                
                # tracing
                print(f"\n[{current_ip}] {op} {arg1} {arg2 if arg2 else ''}")
                print(f"Registers: {self.registers}")
                print(f"Stack: {self.stack}")
                print(f"Heap: {[x for x in self.heap if x is not None]}")
                print(f"Call Stack: {self.call_stack}")

                if op == 'CALL':
                    self.call_stack.append(self.registers['IP'])
                    self.registers['IP'] = self.predicates[arg1]
                elif op == 'PROCEED':
                    self.registers['IP'] = self.call_stack.pop()
                elif op == 'GET_VARIABLE':
                    self.stack.append(('REF', arg1))
                elif op == 'PUT_CONSTANT':
                    self.heap[arg1] = ('CONST', self.constants[arg2])
                elif op == 'UNIFY_VARIABLE':
                    self.heap[arg1] = self.stack.pop()
                elif op == 'PUT_ANY':
                    self.heap[arg1] = ('REF', arg1)
                elif op == 'GET_ANY':
                    new_addr = len(self.heap)
                    self.heap.append(('REF', new_addr))
                    self.stack.append(('REF', new_addr))
                elif op == 'CUT':
                    self.choice_points = self.choice_points[:arg1]
                elif op == 'BUILTIN':
                    self.execute_builtin(arg1)
                elif op == 'HALT':
                    print("\nExecution completed successfully")
                    return
                else:
                    raise ValueError(f"Unknown instruction: {op}")

        except Exception as e:
            print(f"\nERROR AT [{current_ip}] {instr}: {e}")
            raise

    def execute_builtin(self, builtin):
        if builtin == r'\=':
            right = self.stack.pop()
            left = self.stack.pop()
            if left == right:
                # fail if values are equal
                self.registers['IP'] = self.call_stack.pop()
        else:
            raise ValueError(f"Unknown built-in predicate: {builtin}")


class Compiler:
    def __init__(self):
        self.vars = {}        # maps variables (VARIABLES) to indices
        self.constants = {}   # maps constants (lowercase) to indices
        self.predicates = {}  # maps predicates to code addresses
        self.instructions = []

        # register built-in predicates
        self.builtins = {r'\=': self.compile_inequality}

    def compile_inequality(self, args):
        left, right = args

        if left[0].isupper():  # variable, X, Y, etc.
            self.instructions.append(('GET_VARIABLE', self.vars[left], 0))
        else:  # constant, a, b, etc.
            self.instructions.append(('GET_CONSTANT', self.constants[left], 0))
        
        if right[0].isupper():
            self.instructions.append(('GET_VARIABLE', self.vars[right], 0))
        else:
            self.instructions.append(('GET_CONSTANT', self.constants[right], 0))
        
        self.instructions.append(('BUILTIN', r'\=', 0))

    # clauses = program to WAM instructions
    def compile(self, clauses):
        for clause in clauses:
            if clause[0] == ':-':
                self.compile_rule(clause[1], clause[2:])
            elif clause[0] == '?-':
                self.compile_query(clause[1])
            else:
                self.compile_fact(clause)
        # HALT at the end
        self.instructions.append(('HALT', 0, 0))

    # head = parent(X, Y), body = [parent(X, _), !]
    def compile_rule(self, head, body):
        pred_name, pred_args = head[0], head[1:]
        arity = len(pred_args)
        self.predicates[(pred_name, arity)] = len(self.instructions)
        
        print(f"\nCompiling rule {pred_name}/{arity}")
        
        # register all variables from the head
        for arg in pred_args:
            if arg != '_' and arg not in self.vars and arg[0].isupper():
                self.vars[arg] = len(self.vars)
                print(f"  Variable {arg} => v{self.vars[arg]}")

        # register all variables from the body
        for goal in body:
            if isinstance(goal, list):  # skip cut operator '!'
                for arg in goal[1:]:   # skip the functor
                    if arg != '_' and arg not in self.vars and arg[0].isupper():
                        self.vars[arg] = len(self.vars)
                        print(f"  Variable {arg} => v{self.vars[arg]}")

        # compile body
        for goal in body:
            if goal == '!':
                print("  Compiling cut")
                self.instructions.append(('CUT', len(self.vars), 0))
            elif isinstance(goal, list) and goal[0] in self.builtins:
                print(f"  Compiling built-in {goal[0]}")
                # built-in predicates
                self.builtins[goal[0]](goal[1:])
            else:
                self.compile_goal(goal)

        self.instructions.append(('PROCEED', 0, 0))

    # fact = parent(zeb, john)
    def compile_fact(self, fact):
        pred_name, pred_args = fact[0], fact[1:]
        arity = len(pred_args)
        self.predicates[(pred_name, arity)] = len(self.instructions)
        
        print(f"\nCompiling fact {pred_name}/{arity}")
        
        for i, arg in enumerate(pred_args):
            if arg == '_':
                self.instructions.append(('PUT_ANY', i, 0))
            elif isinstance(arg, str) and arg[0].islower():
                if arg not in self.constants:
                    self.constants[arg] = len(self.constants)
                    print(f"  Constant {arg} => c{self.constants[arg]}")
                self.instructions.append(('PUT_CONSTANT', i, self.constants[arg]))
            else:
                raise ValueError(f"Invalid fact argument: {arg}")

        self.instructions.append(('PROCEED', 0, 0))

    # goal = child(X)
    def compile_goal(self, goal):
        pred_name, pred_args = goal[0], goal[1:]
        arity = len(pred_args)
        
        print(f"  Compiling goal {pred_name}/{arity}")
        
        for arg in pred_args:
            if arg == '_':
                self.instructions.append(('GET_ANY', 0, 0))
            elif isinstance(arg, str) and arg[0].islower():
                self.instructions.append(('GET_CONSTANT', self.constants[arg], 0))
            else:
                self.instructions.append(('GET_VARIABLE', self.vars[arg], 0))
        
        self.instructions.append(('CALL', (pred_name, arity), 0))

    # query = child(X)
    def compile_query(self, query):
        print(f"\nCompiling query: {query}")
        
        # register variables in the query
        for arg in query[1:]:  # skip the functor
            if arg != '_' and arg not in self.vars and arg[0].isupper():
                self.vars[arg] = len(self.vars)
                print(f"  Variable {arg} => v{self.vars[arg]}")

        # compile the query as a goal
        self.compile_goal(query)



program = [
    ['parent', 'zeb', 'john'],
    ['parent', 'zeb', 'jane'],
    ['parent', 'john', 'jim'],
    ['parent', 'jane', 'alice'],
    [':-', ['child', 'X'], ['parent', 'X', '_'], '!'],
    [':-', ['grandparent', 'X', 'Z'], ['parent', 'X', 'Y'], ['parent', 'Y', 'Z']],
    [':-', ['sibling', 'X', 'Y'], ['parent', 'Z', 'X'], ['parent', 'Z', 'Y'], [r'\=', 'X', 'Y']],
    ['?-', ['child', 'X']],
    ['?-', ['grandparent', 'zeb', 'Who']],
    ['?-', ['sibling', 'john', 'Sibling']]
]


print("=== COMPILATION ===")
compiler = Compiler()
compiler.compile(program)

print("\n=== COMPILATION RESULTS ===")
print(f"Variables: {compiler.vars}")
print(f"Constants: {compiler.constants}")
print(f"Predicates: {compiler.predicates}")
print("\nGenerated Code:")
for addr, instr in enumerate(compiler.instructions):
    print(f"{addr:3d}: {instr}")

print("\n=== EXECUTION ===")
vm = WAM()
vm.load(compiler)

print("Starting execution with child(X)...")
try:
    # init call stack with HALT
    vm.call_stack.append(len(vm.instructions)-1)  # address of HALT
    # start execution at child/1
    vm.registers['IP'] = vm.predicates[('child', 1)]
    vm.fetch_execute()
except Exception as e:
    print(f"Execution failed: {e}")