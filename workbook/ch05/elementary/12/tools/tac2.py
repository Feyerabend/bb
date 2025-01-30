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
        self.call_stack = []

    def run(self):
        for idx, instr in enumerate(self.tac):
            if instr["op"] == "LABEL":
                self.labels[instr["result"]] = idx

        if "main" in self.labels:
            self.pc = self.labels["main"]
        else:
            self.pc = 0 # ever get here?

        while self.pc < len(self.tac):
            instr = self.tac[self.pc]
            op = instr["op"]
            if op == "LOAD":
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
                self.call_stack.append(self.pc + 1)
                self.pc = self.labels[instr["arg1"]]
                continue
            elif op == "RETURN":
                if self.call_stack:
                    self.pc = self.call_stack.pop()
                    continue
                else:
                    break
            self.pc += 1

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

vm = TACVM(tac)
vm.frames[0].set_var("a", 0)
vm.frames[0].set_var("b", 0)
vm.run()

print("a =", vm.current_frame.get_var("a"))  #  6
print("b =", vm.current_frame.get_var("b"))  #  10
