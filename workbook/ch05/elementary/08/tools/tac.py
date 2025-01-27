
class Frame:
    def __init__(self, name="global"):
        self.name = name      # Scope name (e.g., "global", "computeGCD")
        self.vars = {}        # Variables in this scope
        self.temps = {}       # Temporary variables (t0, t1, ...)

    def get_var(self, name):
        return self.vars.get(name, None)

    def set_var(self, name, value):
        self.vars[name] = value

    def get_temp(self, temp):
        return self.temps.get(temp, None)

    def set_temp(self, temp, value):
        self.temps[temp] = value

class TACVM:
    def __init__(self, tac_instructions):
        self.tac = tac_instructions
        self.pc = 0
        self.frames = [Frame("global")]
        self.current_frame = self.frames[0]
        self.labels = {}             # Labels (L0, L1 ..)
        self.call_stack = []         # Stack of return addresses

    def run(self):
        for idx, instr in enumerate(self.tac):
            if instr["op"] == "LABEL":
                self.labels[instr["result"]] = idx

        while self.pc < len(self.tac):
            instr = self.tac[self.pc]
            op = instr["op"]

            if op == "LOAD":
                # constants ("10") and variables ("a")
                if instr["arg1"].isdigit():
                    value = int(instr["arg1"])
                else:
                    value = self.current_frame.get_var(instr["arg1"])
                self.current_frame.set_temp(instr["result"], value)

            elif op == "+":
                left = self.current_frame.get_temp(instr["arg1"])
                right = self.current_frame.get_temp(instr["arg2"])
                self.current_frame.set_temp(instr["result"], left + right)

            elif op == "=":
                value = self.current_frame.get_temp(instr["arg1"])
                self.current_frame.set_var(instr["result"], value)

            elif op == "CALL":
                # push return address and switch to procedure frame
                self.call_stack.append(self.pc + 1)
                self.pc = self.labels[instr["arg1"]]
                continue

            elif op == "RETURN":
                if self.call_stack:
                    self.pc = self.call_stack.pop()
                    continue
                else:
                    break  # exit if no return address
            self.pc += 1

tac = [
    {"op": "LOAD", "arg1": "10", "result": "t0"},
    {"op": "=", "arg1": "t0", "result": "max"},
    {"op": "LABEL", "result": "main"},
    {"op": "LABEL", "result": "L0"},
    {"op": "LOAD", "arg1": "counter", "result": "t1"},
    {"op": "LOAD", "arg1": "max", "result": "t2"},
    {"op": "<", "arg1": "t1", "arg2": "t2", "result": "t3"},
    {"op": "IF_NOT", "arg1": "t3", "arg2": "L1"},
    {"op": "LOAD", "arg1": "counter", "result": "t4"},
    {"op": "LOAD", "arg1": "1", "result": "t5"},
    {"op": "+", "arg1": "t4", "arg2": "t5", "result": "t6"},
    {"op": "=", "arg1": "t6", "result": "counter"},
    {"op": "GOTO", "arg1": "L0"},
    {"op": "LABEL", "result": "L1"},
]

vm = TACVM(tac)
vm.frames[0].set_var("max", 10)
vm.frames[0].set_var("counter", 0)
vm.run()
print(vm.current_frame.get_var("counter"))  #  10 (after loop)


tac = [
    {"op": "LABEL", "result": "increment_a"},
    {"op": "LOAD", "arg1": "a", "result": "t0"},
    {"op": "LOAD", "arg1": "1", "result": "t1"},
    {"op": "+", "arg1": "t0", "arg2": "t1", "result": "t2"},
    {"op": "=", "arg1": "t2", "result": "a"},
    {"op": "LOAD", "arg1": "10", "result": "t3"},
    {"op": "=", "arg1": "t3", "result": "b"},
    {"op": "RETURN"},
    {"op": "LABEL", "result": "main"},
    {"op": "LOAD", "arg1": "5", "result": "t4"},
    {"op": "=", "arg1": "t4", "result": "a"},
    {"op": "CALL", "arg1": "increment_a"},
]

# Initialize global variables
vm = TACVM(tac)
vm.frames[0].set_var("a", 0)  # a = 0 (initial value)
vm.frames[0].set_var("b", 0)  # b = 0 (initial value)

# Run the VM
vm.run()

# Check the final values of a and b
print("a =", vm.current_frame.get_var("a"))  # Output: a = 6
print("b =", vm.current_frame.get_var("b"))  # Output: b = 10
