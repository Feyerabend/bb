# Simple multiplication library
# Takes two arguments (arg0, arg1) and returns their product in 'result'
math_multiply_library = [
    {"type": "label", "identifier": "multiply"},
    {"type": "assignment", "dest": "result", 
     "rhs": {"type": "binary_op", 
             "left": {"type": "term", "value": "arg0"}, 
             "operator": "*", 
             "right": {"type": "term", "value": "arg1"}}},
    {"type": "return"},
]
