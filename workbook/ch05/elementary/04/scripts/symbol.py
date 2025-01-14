
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
        print("done.")


if __name__ == "__main__":
   main(sys.argv[1:])
