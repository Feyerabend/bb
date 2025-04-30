
class LogicalGate:
    def compute(self, a: int, b: int) -> int:
        raise NotImplementedError

class AndGate(LogicalGate):
    def compute(self, a: int, b: int) -> int:
        return a & b

class OrGate(LogicalGate):
    def compute(self, a: int, b: int) -> int:
        return a | b

class XorGate(LogicalGate):
    def compute(self, a: int, b: int) -> int:
        return a ^ b

def gate_factory(gate_type: str) -> LogicalGate:
    if gate_type == "AND":
        return AndGate()
    elif gate_type == "OR":
        return OrGate()
    elif gate_type == "XOR":
        return XorGate()
    else:
        raise ValueError(f"Unknown gate type: {gate_type}")

class HalfAdder:
    def __init__(self):
        self.xor = gate_factory("XOR")
        self.and_ = gate_factory("AND")

    def compute(self, a: int, b: int):
        sum_ = self.xor.compute(a, b)
        carry = self.and_.compute(a, b)
        return sum_, carry

class FullAdder:
    def __init__(self):
        self.xor = gate_factory("XOR")
        self.and_ = gate_factory("AND")
        self.or_ = gate_factory("OR")

    def compute(self, a: int, b: int, carry_in: int):
        ha1 = HalfAdder()
        ha2 = HalfAdder()

        sum1, carry1 = ha1.compute(a, b)
        final_sum, carry2 = ha2.compute(sum1, carry_in)

        carry_out = self.or_.compute(carry1, carry2)
        return final_sum, carry_out

def add_8bit(a: int, b: int):
    result = 0
    carry = 0
    adder = FullAdder()

    for i in range(8):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        sum_bit, carry = adder.compute(bit_a, bit_b, carry)
        result |= (sum_bit << i)

    carry_out = carry
    return result, carry_out

def print_result(a, b, result, carry_out):
    print(f"Operand A : 0x{a:02X} ({a})")
    print(f"Operand B : 0x{b:02X} ({b})")
    print(f"Sum       : 0x{result:02X} ({result})")
    print(f"Carry out : {carry_out}")

if __name__ == "__main__":
    a = 0xD5  # 213
    b = 0x67  # 103
    result, carry_out = add_8bit(a, b)
    print_result(a, b, result, carry_out)
