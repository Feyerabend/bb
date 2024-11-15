import re

class PostScriptTokenizer:
    def __init__(self):
        self.token_pattern = re.compile(r"""
            (?P<name>/?[a-zA-Z][a-zA-Z0-9_]*)            # Name or keyword with optional '/' prefix
            | (?P<bracketed_list>\[[a-zA-Z0-9_\s!]*\])   # Bracketed list
            | (?P<number>-?[0-9]+)                       # Integer (including negatives)
            | (?P<brace>[}{]+)                           # Curly braces, could be nested
            | (?P<comment>%.*)                           # Comment starting with '%'
            | (?P<symbol>[^\s])                          # Any other non-whitespace character
        """, re.VERBOSE)

    def tokenize(self, s):
        tokens = [match.group(0) for match in self.token_pattern.finditer(s)]
        return tokens

# Helper function to check if a token is an array
def isArray(token):
    return token.startswith('[') and token.endswith(']')

# Group-matching function to handle nested structures
def groupMatching(it):
    res = []
    for token in it:
        if token in ('}', ']'):
            return res  # End of nested structure
        elif token == '{' or token == '[':
            # Recursive call for nested structures
            res.append(groupMatching(it))
        else:
            res.append(parse_token(token))
    return res

# Helper function for parsing arrays
def arrayMatching(array_token):
    array_token = array_token[1:-1]  # Remove enclosing brackets
    return [parse_token(item) for item in array_token.split() if item]

# Parse tokens into structured data
def parse(tokens):
    result = []
    it = iter(tokens)
    for token in it:
        if token in ('}', ']'):
            return False  # Syntax error: unmatched closing brace/bracket
        elif token == '{' or token == '[':
            # Parse a code block or array
            result.append(groupMatching(it))
        else:
            result.append(parse_token(token))
    return result

# Helper function to parse individual tokens into appropriate types
def parse_token(token):
    # Number conversion
    if token.lstrip('-').isdigit():
        return int(token)
    elif token.replace('.', '', 1).lstrip('-').isdigit():
        return float(token)
    elif token == 'true':
        return True
    elif token == 'false':
        return False
    elif isArray(token):  # Array detection
        return arrayMatching(token)
    else:
        return token  # For names and other symbols

# Testing with an example script
tokenizer = PostScriptTokenizer()
example_script = "2 3 add { /variable_name 42 } [1 2 3] % Comment here"
tokens = tokenizer.tokenize(example_script)
parsed_result = parse(tokens)

print(parsed_result)

