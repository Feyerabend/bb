__version__ = "1.0.0"
__author__ = "Educational Example"

# Import main API for easy access
from .api.parser_api import ArithmeticParserAPI

# Make the main class available at package level
__all__ = ['ArithmeticParserAPI']
