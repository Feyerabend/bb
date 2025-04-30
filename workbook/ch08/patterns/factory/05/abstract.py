# Instead of calling `gate_factory()` repeatedly as in method.py,
# we define a factory class that can create a full family of gates
# (AND, OR, XOR).  

# The HalfAdder and FullAdder get all gates from one factory instance
# hence Abstract Factory.


from abc import ABC, abstractmethod

# Abstract Product
class LogicalGate(ABC):
    @abstractmethod
    def operate(self, a: int, b: int) -> int:
        pass

# Concrete Products
class AndGate(LogicalGate):
    def operate(self, a: int, b: int) -> int:
        return a & b

class OrGate(LogicalGate):
    def operate(self, a: int, b: int) -> int:
        return a | b

class XorGate(LogicalGate):
    def operate(self, a: int, b: int) -> int:
        return a ^ b

# Abstract Factory
class GateFactory(ABC):
    @abstractmethod
    def create_and(self) -> LogicalGate:
        pass

    @abstractmethod
    def create_or(self) -> LogicalGate:
        pass

    @abstractmethod
    def create_xor(self) -> LogicalGate:
        pass

# Concrete Factory
class BasicGateFactory(GateFactory):
    def create_and(self) -> LogicalGate:
        return AndGate()

    def create_or(self) -> LogicalGate:
        return OrGate()

    def create_xor(self) -> LogicalGate:
        return XorGate()

class HalfAdder:
    def __init__(self, factory: GateFactory):
        self.xor = factory.create_xor()
        self.and_ = factory.create_and()

    def compute(self, a: int, b: int) -> (int, int):
        sum_ = self.xor.operate(a, b)
        carry = self.and_.operate(a, b)
        return sum_, carry

class FullAdder:
    def __init__(self, factory: GateFactory):
        self.ha1 = HalfAdder(factory)
        self.ha2 = HalfAdder(factory)
        self.or_ = factory.create_or()

    def compute(self, a: int, b: int, cin: int) -> (int, int):
        sum1, carry1 = self.ha1.compute(a, b)
        sum2, carry2 = self.ha2.compute(sum1, cin)
        cout = self.or_.operate(carry1, carry2)
        return sum2, cout

def add_8bit(a: int, b: int, factory: GateFactory) -> (int, int):
    full_adders = [FullAdder(factory) for _ in range(8)]

    sum_ = 0
    carry = 0
    for i in range(8):
        a_bit = (a >> i) & 1
        b_bit = (b >> i) & 1
        s, carry = full_adders[i].compute(a_bit, b_bit, carry)
        sum_ |= (s << i)
    return sum_ & 0xFF, carry

if __name__ == "__main__":
    factory = BasicGateFactory()

    a = 0xD5  # 213
    b = 0x67  # 103
    result, carry_out = add_8bit(a, b, factory)

    print(f"Operand A : 0x{a:02X} ({a})")
    print(f"Operand B : 0x{b:02X} ({b})")
    print(f"Sum       : 0x{result:02X} ({result})")
    print(f"Carry out : {carry_out}")
