import re

def tokenize(s):
    # Define separate regex patterns for different types of tokens
    name_pattern = re.compile(r"/?[a-zA-Z][a-zA-Z0-9_]*")  # Name or keyword starting with a letter, may have prefix '/'
    bracketed_list_pattern = re.compile(r"\[[a-zA-Z0-9_\s!]*\]")  # Bracketed list
    number_pattern = re.compile(r"-?[0-9]+")  # Integer numbers
    brace_pattern = re.compile(r"[}{]+")  # Curly braces
    comment_pattern = re.compile(r"%.*")  # Comment starting with '%'
    symbol_pattern = re.compile(r"[^\s]")  # Any other non-whitespace character

    # Combine all patterns
    patterns = [
        name_pattern,
        bracketed_list_pattern,
        number_pattern,
        brace_pattern,
        comment_pattern,
        symbol_pattern
    ]

    # Initialize token list
    tokens = []

    # Process the input string to find all matches from each pattern in order
    pos = 0
    while pos < len(s):
        for pattern in patterns:
            match = pattern.match(s, pos)
            if match:
                tokens.append(match.group(0))
                pos = match.end()  # Move position to end of current match
                break
        else:
            pos += 1  # If no pattern matches, move to the next character

    return tokens


#tokenizer was provided by professor
import re
def tokenize2(s):
    return re.findall("/?[a-zA-Z][a-zA-Z0-9_]*|[[][a-zA-Z0-9_\s!][a-zA-Z0-9_\s!]*[]]|[-]?[0-9]+|[}{]+|%.*|[^ \t\n]", s)


print(tokenize2("/square {dup mul} def [1 2 3 4] {square} forall add add add 30 eq stack"))

print(tokenize2("/square {dup mul} def [1 2 3 4] {square} forall add add add 30 eq stack"))

import re

class PostScriptTokenizer:
    """
    Tokenizer for PostScript-like syntax, handling names, brackets, numbers,
    braces, comments, and other symbols with nesting robustness.
    """

    def __init__(self):
        # Compile the combined pattern with named groups for clarity
        self.token_pattern = re.compile(r"""
            (?P<name>/?[a-zA-Z][a-zA-Z0-9_]*)             # Name or keyword with optional '/' prefix
            | (?P<bracketed_list>\[[a-zA-Z0-9_\s!]*\])    # Bracketed list
            | (?P<number>-?[0-9]+)                         # Integer (including negatives)
            | (?P<brace>[}{]+)                             # Curly braces, could be nested
            | (?P<comment>%.*)                             # Comment starting with '%'
            | (?P<symbol>[^\s])                            # Any other non-whitespace character
        """, re.VERBOSE)
    
    def tokenize(self, s):
        """
        Tokenizes the input string, returning a list of tokens with detailed handling.
        """
        tokens = []
        position = 0  # Track position for nesting and error reporting

        # Iterate over matches using the compiled regex pattern
        for match in self.token_pattern.finditer(s):
            token = match.group(0)
            token_type = match.lastgroup  # Identify the matched group type

            # Process each type explicitly, allowing nested structures
            if token_type == 'name':
                tokens.append(self.process_name(token))
            elif token_type == 'bracketed_list':
                tokens.append(self.process_bracketed_list(token))
            elif token_type == 'number':
                tokens.append(self.process_number(token))
            elif token_type == 'brace':
                tokens.append(self.process_brace(token))
            elif token_type == 'comment':
                self.process_comment(token)  # Comments typically ignored in output
            elif token_type == 'symbol':
                tokens.append(token)  # Directly add symbols
            
            position = match.end()  # Update position for error handling

        return tokens

    def process_name(self, token):
        """
        Processes name or keyword tokens, with optional handling for `/` prefix.
        """
        return token  # In PostScript, names often don't need transformation

    def process_bracketed_list(self, token):
        """
        Handles bracketed lists, assuming balanced brackets.
        """
        # Process bracketed content (e.g., stripping brackets)
        return token  # For now, return the list as-is; could further parse contents

    def process_number(self, token):
        """
        Converts numeric tokens to integers or floats as appropriate.
        """
        return int(token) if '.' not in token else float(token)

    def process_brace(self, token):
        """
        Handles braces, which may require nesting awareness.
        """
        # Return braces; could add stack-based check if needed for deeper nesting
        return token

    def process_comment(self, token):
        """
        Ignores comments, allowing extension for logging if needed.
        """
        # For extensibility, could log comments or handle them differently
        pass


# Testing the detailed tokenizer
tokenizer = PostScriptTokenizer()
example_script = "2 3 add { /variable_name 42 } % Comment here"
tokens = tokenizer.tokenize(example_script)

tokens

