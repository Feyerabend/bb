# Simple addition library
# Takes two arguments (arg0, arg1) and returns their sum in 'result'
math_add_library = [
    {"type": "label", "identifier": "add"},
    {"type": "assignment", "dest": "result", 
     "rhs": {"type": "binary_op", 
             "left": {"type": "term", "value": "arg0"}, 
             "operator": "+", 
             "right": {"type": "term", "value": "arg1"}}},
    {"type": "return"},
]
