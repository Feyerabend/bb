class Frame:
    def __init__(self, name="global"):
        self.name = name
        self.vars = {}
        self.temps = {}

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
        self.labels = {}
        self.call_stack = []  # (return_pc, previous_frame)

    def get_variable(self, name):
        # Check local frame first
        value = self.current_frame.get_var(name)
        if value is not None:
            return value
        # fall back to global frame
        return self.frames[0].get_var(name)

    def set_variable(self, name, value, force_global=False):
        if force_global:
            # update global variable
            self.frames[0].set_var(name, value)
        else:
            # default: set in current frame
            self.current_frame.set_var(name, value)

    def run(self):
        for idx, instr in enumerate(self.tac):
            if instr["op"] == "LABEL":
                self.labels[instr["result"]] = idx

        self.pc = self.labels.get("main", 0)

        while self.pc < len(self.tac):
            instr = self.tac[self.pc]
            op = instr["op"]

            if op == "LOAD":
                if instr["arg1"].isdigit():
                    value = int(instr["arg1"])
                else:
                    value = self.get_variable(instr["arg1"])
                self.current_frame.set_temp(instr["result"], value)

            elif op in ("+", "-", "!=", ">", "<="):
                left = self.current_frame.get_temp(instr["arg1"])
                right = self.current_frame.get_temp(instr["arg2"])
                if op == "+":
                    result = left + right
                elif op == "-":
                    result = left - right
                elif op == "!=":
                    result = 1 if left != right else 0
                elif op == ">":
                    result = 1 if left > right else 0
                elif op == "<=":
                    result = 1 if left <= right else 0
                self.current_frame.set_temp(instr["result"], result)

            elif op == "=":
                value = self.current_frame.get_temp(instr["arg1"])
                self.set_variable(instr["result"], value)

            elif op == "GLOBAL=":  # operation for explicit global assignment
                value = self.current_frame.get_temp(instr["arg1"])
                self.set_variable(instr["result"], value, force_global=True)

            elif op == "IF_NOT":
                if not self.current_frame.get_temp(instr["arg1"]):
                    self.pc = self.labels[instr["result"]]
                    continue

            elif op == "GOTO":
                self.pc = self.labels[instr["result"]]
                continue

            elif op == "CALL":
                self.call_stack.append((self.pc + 1, self.current_frame))
                new_frame = Frame(instr["arg1"])
                self.frames.append(new_frame)
                self.current_frame = new_frame
                self.pc = self.labels[instr["arg1"]]
                continue

            elif op == "RETURN":
                if self.call_stack:
                    ret_pc, prev_frame = self.call_stack.pop()
                    self.frames.pop()
                    self.current_frame = prev_frame
                    self.pc = ret_pc
                    continue
                else:
                    break

            self.pc += 1

# Global 'x' modified inside a procedure
tac = [

    # Global 'x' initialized to 10
    {"op": "LABEL", "result": "main"},
    {"op": "LOAD", "arg1": "10", "result": "t0"},
    {"op": "=", "arg1": "t0", "result": "x"},

    # Call function 'modifyGlobals'
    {"op": "CALL", "arg1": "modifyGlobals"},
    {"op": "RETURN"},


    # Function 'modifyGlobals'
    {"op": "LABEL", "result": "modifyGlobals"},

    # Local 'x' = 20 (shadows global)
    {"op": "LOAD", "arg1": "20", "result": "t1"},
    {"op": "=", "arg1": "t1", "result": "x"},

    # Local 'y' = 90 (new variable)
    {"op": "LOAD", "arg1": "90", "result": "t3"},
    {"op": "=", "arg1": "t3", "result": "y"},

    # Explicitly update global 'x' to 30
    {"op": "LOAD", "arg1": "30", "result": "t2"},
    {"op": "GLOBAL=", "arg1": "t2", "result": "x"},
    {"op": "RETURN"},
]

vm = TACVM(tac)
vm.frames[0].set_var("x", 0)  # init global 'x'
vm.run()


print("Global x =", vm.frames[0].get_var("x"))  #  x = 30
for f in vm.frames:
    print(f.name, f.vars)  # global frame remains: {'x': 30}
