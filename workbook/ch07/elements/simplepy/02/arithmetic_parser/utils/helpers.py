def is_number(value: str) -> bool:
    """Check if a string represents a number."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def safe_divide(a: float, b: float) -> float:
    """Safely divide two numbers."""
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return a / b
