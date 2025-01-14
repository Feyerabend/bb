
import sys
import json
import getopt

def extract_symbols(ast, current_scope=None, global_scope=None):
    if global_scope is None:
        global_scope = {}  # The global symbol table
    if current_scope is None:
        current_scope = global_scope  # Initially, the global scope is the current scope
    
    if isinstance(ast, dict):
        # Handling different node types

        if ast.get("type") == "VAR_DECL":
            # Variable declaration - Add it to the current scope
            var_name = ast.get("value")
            current_scope[var_name] = {"type": "variable"}
        
        elif ast.get("type") == "PROC_DECL":
            # Procedure declaration - create a new scope for the procedure
            proc_name = ast.get("value")
            proc_scope = {}  # New scope for the procedure's variables
            current_scope[proc_name] = {"type": "procedure", "scope": proc_scope}

            # Recurse into the procedure block to process local variables
            for child in ast.get("children", []):
                extract_symbols(child, current_scope=proc_scope, global_scope=global_scope)
        
        elif ast.get("type") == "BEGIN" or ast.get("type") == "BLOCK":
            # Block - create a new scope for the block
            block_scope = {}  # New scope for the block
            for child in ast.get("children", []):
                extract_symbols(child, current_scope=block_scope, global_scope=global_scope)
        
        elif ast.get("type") == "IDENTIFIER":
            # Add the identifier to the current scope if not already declared
            identifier_name = ast.get("value")
            if identifier_name not in current_scope:
                current_scope[identifier_name] = {"type": "variable"}

        # Recursively handle children nodes
        for child in ast.get("children", []):
            extract_symbols(child, current_scope=current_scope, global_scope=global_scope)

    return global_scope

def print_symbol_relationships(ast, symbol_table, scope_stack=None):
    if scope_stack is None:
        scope_stack = ["global"]

    # Handling different node types in the AST
    if isinstance(ast, dict):
        if ast.get("type") == "VAR_DECL":
            # Variable declaration - Add to symbol table and print out the relationship with the scope
            var_name = ast.get("value")
            current_scope = scope_stack[-1]
            if current_scope not in symbol_table:
                symbol_table[current_scope] = {"variables": [], "procedures": []}
            symbol_table[current_scope]["variables"].append(var_name)
            print(f"Variable '{var_name}' declared in scope '{current_scope}'.")

        elif ast.get("type") == "PROC_DECL":
            # Procedure declaration - Add to symbol table and print out the relationship with the scope
            proc_name = ast.get("value")
            current_scope = scope_stack[-1]
            if current_scope not in symbol_table:
                symbol_table[current_scope] = {"variables": [], "procedures": []}
            symbol_table[current_scope]["procedures"].append(proc_name)
            print(f"Procedure '{proc_name}' declared in scope '{current_scope}'.")

            # Recurse into the procedure block to print relationships for local variables
            for child in ast.get("children", []):
                print_symbol_relationships(child, symbol_table, scope_stack)

        elif ast.get("type") == "BEGIN" or ast.get("type") == "BLOCK":
            # Block - process its scope
            block_scope = f"{scope_stack[-1]}_block"
            scope_stack.append(block_scope)
            print(f"Entering block scope '{block_scope}' from scope '{scope_stack[-2]}'.")

            for child in ast.get("children", []):
                print_symbol_relationships(child, symbol_table, scope_stack)

            # After processing the block, we exit the scope
            print(f"Exiting block scope '{block_scope}'.")
            scope_stack.pop()

        elif ast.get("type") == "IDENTIFIER":
            # Identifier usage - Print its relationship with the scope
            identifier_name = ast.get("value")
            current_scope = scope_stack[-1]
            if current_scope in symbol_table and identifier_name in symbol_table[current_scope]["variables"]:
                print(f"Identifier '{identifier_name}' used in scope '{current_scope}'.")
            elif current_scope in symbol_table and identifier_name in symbol_table[current_scope]["procedures"]:
                print(f"Procedure '{identifier_name}' used in scope '{current_scope}'.")

        # Recursively handle children nodes
        for child in ast.get("children", []):
            print_symbol_relationships(child, symbol_table, scope_stack)


def main(argv):
    inputfile = ''
    outputfile = ''
    verbose = 0

    try:
        opts, args = getopt.getopt(argv,"vhi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('symbol.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-v':
            verbose = 1
        if opt == '-h':
            print('usage: symbol.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg


    if verbose == 1:
        print("symbol table gen ..")

    with open(inputfile, 'r') as input_file:
        ast = json.load(input_file)

    global_scope = extract_symbols(ast)

    with open(outputfile, 'w') as output_file:
        json.dump(global_scope, output_file, indent=4)

    if verbose == 1:
        print_symbol_relationships(ast, global_scope)
        print("done.")


if __name__ == "__main__":
   main(sys.argv[1:])
