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

        self.pc = self.labels.get("main", 0)

        while self.pc < len(self.tac):
            instr = self.tac[self.pc]
            op = instr["op"]
            
            if op == "LOAD":
                value = int(instr["arg1"]) if instr["arg1"].isdigit() else self.current_frame.get_var(instr["arg1"])
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
                self.current_frame.set_var(instr["result"], value)
            
            elif op == "IF_NOT":
                if not self.current_frame.get_temp(instr["arg1"]):
                    self.pc = self.labels[instr["result"]]
                    continue
            
            elif op == "GOTO":
                self.pc = self.labels[instr["result"]]
                continue
            
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
    {"op": "LABEL", "result": "computeGCD"},
    {"op": "LABEL", "result": "L0"},
    {"op": "LOAD", "arg1": "b", "result": "t0"},
    {"op": "LOAD", "arg1": "0", "result": "t1"},
    {"op": "!=", "arg1": "t0", "arg2": "t1", "result": "t2"},
    {"op": "IF_NOT", "arg1": "t2", "result": "L1"},
    {"op": "LOAD", "arg1": "a", "result": "t3"},
    {"op": "LOAD", "arg1": "b", "result": "t4"},
    {"op": ">", "arg1": "t3", "arg2": "t4", "result": "t5"},
    {"op": "IF_NOT", "arg1": "t5", "result": "L2"},
    {"op": "LOAD", "arg1": "a", "result": "t6"},
    {"op": "LOAD", "arg1": "b", "result": "t7"},
    {"op": "-", "arg1": "t6", "arg2": "t7", "result": "t8"},
    {"op": "=", "arg1": "t8", "result": "a"},
    {"op": "LABEL", "result": "L2"},
    {"op": "LOAD", "arg1": "a", "result": "t9"},
    {"op": "LOAD", "arg1": "b", "result": "t10"},
    {"op": "<=", "arg1": "t9", "arg2": "t10", "result": "t11"},
    {"op": "IF_NOT", "arg1": "t11", "result": "L3"},
    {"op": "LOAD", "arg1": "b", "result": "t12"},
    {"op": "LOAD", "arg1": "a", "result": "t13"},
    {"op": "-", "arg1": "t12", "arg2": "t13", "result": "t14"},
    {"op": "=", "arg1": "t14", "result": "b"},
    {"op": "LABEL", "result": "L3"},
    {"op": "GOTO", "result": "L0"},
    {"op": "LABEL", "result": "L1"},
    {"op": "LOAD", "arg1": "a", "result": "t15"},
    {"op": "=", "arg1": "t15", "result": "gcd"},
    {"op": "RETURN"},
    {"op": "LABEL", "result": "main"},
    {"op": "LOAD", "arg1": "48", "result": "t16"},
    {"op": "=", "arg1": "t16", "result": "a"},
    {"op": "LOAD", "arg1": "18", "result": "t17"},
    {"op": "=", "arg1": "t17", "result": "b"},
    {"op": "CALL", "arg1": "computeGCD"},
]

vm = TACVM(tac)
vm.run()

print("GCD =", vm.current_frame.get_var("gcd"))  # GCD = 6
print("a =", vm.current_frame.get_var("a"))      # a = 6
print("b =", vm.current_frame.get_var("b"))      # b = 0
