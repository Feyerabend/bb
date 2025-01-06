factorial_library = [
    {"type": "label", "identifier": "factorial"},
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "1"}},  # start at 1
    {"type": "label", "identifier": "loop_start"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "arg0"}, "operator": "<", "right": {"type": "term", "value": "2"}}, "label": "end_loop"},  # if arg0 <= 1, end loop
    {"type": "assignment", "dest": "result", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "result"}, "operator": "*", "right": {"type": "term", "value": "arg0"}}},  # multiply result by arg0
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "arg0"}, "operator": "-", "right": {"type": "term", "value": "1"}}},  # decrement arg0
    {"type": "goto", "label": "loop_start"},  # repeat loop, again
    {"type": "label", "identifier": "end_loop"},
    {"type": "return"},
]
