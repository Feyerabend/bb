class FixedPoint:
    FRACTIONAL_BITS = 16
    SCALE = 1 << FRACTIONAL_BITS  # 2^16 = 65536

    def __init__(self, value=0):
        """Initialize with an integer, float, or another fixed-point number."""
        if isinstance(value, FixedPoint):
            self.value = value.value
        elif isinstance(value, (int, float)):
            self.value = int(value * self.SCALE)
        else:
            raise ValueError("Unsupported type for FixedPoint initialization.")

    def to_float(self):
        """Convert the fixed-point number to a float."""
        return self.value / self.SCALE

    def __add__(self, other):
        """Addition of two fixed-point numbers."""
        return FixedPoint((self.value + self._get_raw_value(other)) / self.SCALE)

    def __sub__(self, other):
        """Subtraction of two fixed-point numbers."""
        return FixedPoint((self.value - self._get_raw_value(other)) / self.SCALE)

    def __mul__(self, other):
        """Multiplication of two fixed-point numbers."""
        raw_result = (self.value * self._get_raw_value(other)) >> self.FRACTIONAL_BITS
        return FixedPoint(raw_result / self.SCALE)

    def __truediv__(self, other):
        """Division of two fixed-point numbers."""
        raw_result = (self.value << self.FRACTIONAL_BITS) // self._get_raw_value(other)
        return FixedPoint(raw_result / self.SCALE)

    def _get_raw_value(self, other):
        """Extract the raw fixed-point value from another FixedPoint or a float/int."""
        if isinstance(other, FixedPoint):
            return other.value
        elif isinstance(other, (int, float)):
            return int(other * self.SCALE)
        else:
            raise ValueError("Unsupported type for arithmetic operations.")

    def __repr__(self):
        """String representation showing fixed-point value and equivalent float."""
        return f"FixedPoint(value={self.value}, float_equiv={self.to_float():.6f})"


# Example mathematical function
def sqrt_fixed(fp):
    """Fixed-point square root using the Newton-Raphson method."""
    if fp.value < 0:
        raise ValueError("Square root of a negative number is not defined.")
    x = fp.value
    result = x
    while True:
        next_result = (result + (x << FixedPoint.FRACTIONAL_BITS) // result) >> 1
        if abs(result - next_result) < 1:
            break
        result = next_result
    return FixedPoint(result / FixedPoint.SCALE)

