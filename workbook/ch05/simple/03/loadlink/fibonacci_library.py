fibonacci_library = [
    {"type": "label", "identifier": "fibonacci"},
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "0"}},  # F(0) = 0
    {"type": "assignment", "dest": "previous", "rhs": {"type": "term", "value": "1"}},  # F(1) = 1
    {"type": "label", "identifier": "loop_start"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "arg0"}, "operator": "<", "right": {"type": "term", "value": "2"}}, "label": "end_loop"},  # If arg0 <= 1, end loop
    {"type": "assignment", "dest": "temp", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "result"}, "operator": "+", "right": {"type": "term", "value": "previous"}}},  # result = previous + result
    {"type": "assignment", "dest": "previous", "rhs": {"type": "term", "value": "result"}},  # previous = result
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "temp"}},  # result = temp
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "arg0"}, "operator": "-", "right": {"type": "term", "value": "1"}}},  # Decrement arg0
    {"type": "goto", "label": "loop_start"},  # Repeat loop
    {"type": "label", "identifier": "end_loop"},
    {"type": "return"},
]
