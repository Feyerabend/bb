# Simple max library
# Takes two arguments (arg0, arg1) and returns the larger one in 'result'
math_max_library = [
    {"type": "label", "identifier": "max"},
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "arg0"}},  # assume arg0 is max
    {"type": "if", 
     "condition": {"type": "binary_op", 
                   "left": {"type": "term", "value": "arg1"}, 
                   "operator": ">", 
                   "right": {"type": "term", "value": "arg0"}}, 
     "label": "arg1_is_larger"},
    {"type": "goto", "label": "done"},
    {"type": "label", "identifier": "arg1_is_larger"},
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "arg1"}},
    {"type": "label", "identifier": "done"},
    {"type": "return"},
]
