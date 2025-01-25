from collections import namedtuple

State = namedtuple('State', ('stack', 'environment', 'control', 'dump'))


def ADD_command(stack, env, control, dump):
    stack.append(stack.pop() + stack.pop())

def SUB_command(stack, env, control, dump):
    stack.append(stack.pop() - stack.pop())

def MUL_command(stack, env, control, dump):
    stack.append(stack.pop() * stack.pop())

def DIV_command(stack, env, control, dump):
    stack.append(stack.pop() / stack.pop())

def EQ_command(stack, env, control, dump):
    stack.append(stack.pop() == stack.pop())

def LT_command(stack, env, control, dump):
    stack.append(stack.pop() < stack.pop())

def GT_command(stack, env, control, dump):
    stack.append(stack.pop() > stack.pop())

def POP_command(stack, env, control, dump):
    stack.pop()

def DUP_command(stack, env, control, dump):
    stack.append(stack[-1])

def SWAP_command(stack, env, control, dump):
    stack.append(stack.pop(-2))

def CONS_command(stack, env, control, dump):
    stack.append([stack.pop(), stack.pop()])

def CAR_command(stack, env, control, dump):
    stack.append(stack.pop()[0])

def CDR_command(stack, env, control, dump):
    stack.append(stack.pop()[1])

def NIL_command(stack, env, control, dump):
    stack.append([])

def ATOM_command(stack, env, control, dump):
    stack.append(not isinstance(stack.pop(), list))

def SEL_command(stack, env, control, dump):
    condition = stack.pop()
    then_branch = control.pop(0)
    else_branch = control.pop(0)
    control[:] = then_branch if condition else else_branch

def JOIN_command(stack, env, control, dump):
    control.extend(dump.pop())

def RTN_command(stack, env, control, dump):
    result = stack.pop()
    control.clear()
    control.extend(dump.pop())
    new_stack = dump.pop()
    new_stack.append(result)
    stack[:] = new_stack

def LD_command(stack, env, control, dump):
    if env and env[-1]:
        stack.append(env[-1][-1])
    else:
        raise IndexError("Environment is empty")

def LDC_command(stack, env, control, dump):
    if control:
        stack.append(control.pop(0))
    else:
        raise IndexError("Control list is empty")

def LDF_command(stack, env, control, dump):
    if control:
        func_code = control.pop(0)
        stack.append([func_code, env.copy()])  # current environment is closure
    else:
        raise IndexError("Control list is empty")

def AP_command(stack, env, control, dump):
    if len(stack) < 1:
        raise ValueError("AP requires a function on the stack")
    func = stack.pop()
    func_code, closure_env = func[0], func[1]
    # save current state to dump
    dump.append(control.copy())
    dump.append(stack.copy())
    dump.append(env.copy())
    # set new control to function code
    control.clear()
    control.extend(func_code)
    # update environment with closure
    env[:] = closure_env

def RAP_command(stack, env, control, dump):
    # similar to AP but for recursive functions; placeholder implementation
    AP_command(stack, env, control, dump)

def DUM_command(env, *args):
    env.append([])

COMMANDS = {
    'ADD': ADD_command,
    'SUB': SUB_command,
    'MUL': MUL_command,
    'DIV': DIV_command,
    'EQ': EQ_command,
    'LT': LT_command,
    'GT': GT_command,
    'POP': POP_command,
    'DUP': DUP_command,
    'SWAP': SWAP_command,
    'CONS': CONS_command,
    'CAR': CAR_command,
    'CDR': CDR_command,
    'NIL': NIL_command,
    'ATOM': ATOM_command,
    'SEL': SEL_command,
    'JOIN': JOIN_command,
    'RTN': RTN_command,
    'LD': LD_command,
    'LDC': LDC_command,
    'LDF': LDF_command,
    'AP': AP_command,
    'RAP': RAP_command,
    'DUM': DUM_command,
}


def secd_eval(code):
    state = State([], [], code.copy(), [])
    while state.control:
        state = secd_step(state)
    return state.stack[-1] if state.stack else None

def secd_step(state):
    stack, env, control, dump = state
    if not control:
        return state

    cmd = control.pop(0)

    print(f"Executing: {cmd} | Control: {control}")

    if cmd in COMMANDS:
        COMMANDS[cmd](stack, env, control, dump)
    elif isinstance(cmd, (int, float, str)):
        stack.append(cmd)
    else:
        raise ValueError(f"Unknown command: {cmd}")

    return State(stack, env, control, dump)

# Tests
if __name__ == "__main__":

    # Test 1: Simple arithmetic
    code1 = ['LDC', 5, 'LDC', 3, 'ADD']
    print("\nTest 1 (5 + 3):")
    print("Result:", secd_eval(code1))  # Expected: 8

    # Test 2: List operations
    code2 = ['LDC', 1, 'LDC', 2, 'CONS', 'LDC', 3, 'CONS', 'CAR']
    print("\nTest 2 (CAR (CONS 3 (CONS 2 1))):")
    print("Result:", secd_eval(code2))  # Expected: 3

    # Test 3: Conditional (SEL)
    code3 = [
        'LDC', True, 
        'SEL', 
        ['LDC', 10],  # Then branch
        ['LDC', 20]   # Else branch
    ]
    print("\nTest 3 (SEL True 10 20):")
    print("Result:", secd_eval(code3))  # Expected: 10

    # Test 4: Function application (LDF, AP)
    #code4 = ['LDF', ['ADD', 'RTN'], 'LDC', 5, 'LDC', 3, 'AP']
    code4 = ['LDC', 5, 'LDC', 3, 'LDF', ['ADD', 'RTN'], 'AP']
    print("\nTest 4 (LDF [ADD RTN] 5 3 AP):")
    print("Result:", secd_eval(code4))  # Expected: 8

    # Test 5: Recursive function (factorial)
    code5 = [
        'LDC', 5,  # argument first
        'LDF', [   # closure on top
            'DUP', 'LDC', 1, 'EQ', 'SEL', 
            ['POP', 'LDC', 1, 'RTN'], 
            ['DUP', 'LDC', 1, 'SUB', 'LDF', 'AP', 'MUL', 'RTN']
        ],
        'AP'  # apply closure to argument `5`
    ]
    print("\nTest 5 (Factorial of 5):")
    print("Result:", secd_eval(code5))  # Expected: 120

    # Test 6: Stack manipulation (SWAP)
    code6 = ['LDC', 1, 'LDC', 2, 'SWAP', 'ADD']
    print("\nTest 6 (SWAP 1 2 ADD):")
    print("Result:", secd_eval(code6))  # Expected: 3
