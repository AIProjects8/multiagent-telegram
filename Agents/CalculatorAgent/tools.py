from langchain_core.tools import tool
import math

def _round_result(value: float, precision: int = 10) -> float:
    return round(value, precision)

@tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    return _round_result(a + b)

@tool
def subtract(a: float, b: float) -> float:
    """Subtracts the second number from the first number."""
    return _round_result(a - b)

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return _round_result(a * b)

@tool
def divide(a: float, b: float) -> float:
    """Divides the first number by the second number. Raises an error if dividing by zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return _round_result(a / b)

@tool
def pow(a: float, b: float) -> float:
    """Raises the first number to the power of the second number."""
    return _round_result(math.pow(a, b))

@tool
def sqrt(a: float) -> float:
    """Calculates the square root of a number. Raises an error if the number is negative."""
    if a < 0:
        raise ValueError("Square root of negative number is not allowed")
    return _round_result(math.sqrt(a))

