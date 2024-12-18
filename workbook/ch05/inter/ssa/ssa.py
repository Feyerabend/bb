from collections import defaultdict

def constant_folding(ssa_code):
    """Perform constant folding optimization."""
    optimized_code = []
    for line in ssa_code:
        var, expr = line.split(" = ")
        if expr.isdigit():  # Already a constant
            optimized_code.append(line)
            continue
        
        tokens = expr.split()
        if len(tokens) == 3:  # Binary operation
            arg1, op, arg2 = tokens
            if arg1.isdigit() and arg2.isdigit():
                # Evaluate constant expressions
                result = eval(f"{arg1} {op} {arg2}")
                optimized_code.append(f"{var} = {result}")
            else:
                optimized_code.append(line)
        else:
            optimized_code.append(line)
    return optimized_code

def common_subexpression_elimination(ssa_code):
    """Eliminate redundant calculations."""
    expr_to_var = {}
    optimized_code = []
    for line in ssa_code:
        var, expr = line.split(" = ")
        if expr in expr_to_var:
            # Replace with the existing variable
            optimized_code.append(f"{var} = {expr_to_var[expr]}")
        else:
            expr_to_var[expr] = var
            optimized_code.append(line)
    return optimized_code

def dead_code_elimination(ssa_code, live_variables):
    """Remove dead code (unused variables)."""
    optimized_code = []
    for line in reversed(ssa_code):  # Process in reverse to identify live variables
        var, _ = line.split(" = ")
        if var in live_variables:
            optimized_code.append(line)
            # Mark any variables in the RHS as live
            live_variables.update(line.split(" = ")[1].split())
    return list(reversed(optimized_code))

def ssa_to_non_ssa(ssa_code):
    """Convert SSA back to non-SSA form by resolving phi functions."""
    non_ssa_code = []
    for line in ssa_code:
        if "phi" in line:
            # Resolve phi function (for simplicity, assume a sequential assignment)
            var, phi_expr = line.split(" = ")
            choices = phi_expr.strip("phi()").split(", ")
            # Generate conditional assignments based on the phi arguments
            for i, choice in enumerate(choices):
                non_ssa_code.append(f"{var}_v{i} = {choice}")
            non_ssa_code.append(f"{var} = {var}_v{len(choices) - 1}")  # Final assignment
        else:
            non_ssa_code.append(line)
    return non_ssa_code

def optimize_ssa(ssa_code):
    """Run optimizations on SSA code."""
    print("\nOriginal SSA Code:")
    for line in ssa_code:
        print(line)
    
    # Constant folding
    ssa_code = constant_folding(ssa_code)
    print("\nAfter Constant Folding:")
    for line in ssa_code:
        print(line)
    
    # Common subexpression elimination
    ssa_code = common_subexpression_elimination(ssa_code)
    print("\nAfter Common Subexpression Elimination:")
    for line in ssa_code:
        print(line)
    
    # Dead code elimination
    live_variables = {"z"}  # Assume the final result is stored in 'z'
    ssa_code = dead_code_elimination(ssa_code, live_variables)
    print("\nAfter Dead Code Elimination:")
    for line in ssa_code:
        print(line)
    
    return ssa_code

# Test SSA optimization and conversion
def main():
    # Sample SSA code
    ssa_code = [
        "t0 = 5 + 3",
        "t1 = t0 * 2",
        "t2 = 5 + 3",  # Redundant computation
        "t3 = t1 + t2",
        "z = phi(t3, t1)"  # Placeholder phi function
    ]
    
    # Optimize SSA
    optimized_code = optimize_ssa(ssa_code)
    
    # Convert out of SSA
    non_ssa_code = ssa_to_non_ssa(optimized_code)
    print("\nConverted out of SSA:")
    for line in non_ssa_code:
        print(line)

if __name__ == "__main__":
    main()
