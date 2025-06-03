def format_result(result: float, precision: int = 4) -> str:
    """Format numerical result for display."""
    if result == int(result):
        return str(int(result))
    return f"{result:.{precision}f}"