import sys
import json
import getopt

def yaml_format(data, indent=0):
    yaml_lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            yaml_lines.append(f"{' ' * indent}{key}:")
            yaml_lines.extend(yaml_format(value, indent=indent + 2))
        else:
            yaml_lines.append(f"{' ' * indent}{key}: {value}")
    return yaml_lines

def extract_symbols(ast, global_scope=None, scope_stack=None):
    if global_scope is None:
        global_scope = {"variables": {}, "procedures": {}}
    if scope_stack is None:
        scope_stack = [global_scope]

    current_scope = scope_stack[-1]

    if isinstance(ast, dict):
        node_type = ast.get("type")

        if node_type == "VAR_DECL":
            var_name = ast.get("value")
            if var_name in current_scope["variables"]:
                print(f"Warning: Variable '{var_name}' redeclared in the same scope.")
            else:

                # global or local
                scope_type = "global" if len(scope_stack) == 1 else "local"
                current_scope["variables"][var_name] = {"type": "variable", "scope": scope_type}
                print(f"Declared {scope_type} variable: {var_name}.")

        elif node_type == "PROC_DECL":
            proc_name = ast.get("value")
            if proc_name in global_scope["procedures"]:
                print(f"Warning: Procedure '{proc_name}' redeclared in the global scope.")
            else:
                global_scope["procedures"][proc_name] = {"type": "procedure", "scope": {}}
                print(f"Declared procedure: {proc_name} with its own scope.")

            # new scope for procedure
            proc_scope = {"variables": {}}
            global_scope["procedures"][proc_name]["scope"] = proc_scope
            scope_stack.append(proc_scope)

            # children nodes in the procedure's scope
            for child in ast.get("children", []):
                extract_symbols(child, global_scope, scope_stack)

            # pop the procedure's scope when done
            scope_stack.pop()

        elif node_type == "IDENTIFIER":
            var_name = ast.get("value")
            resolved_scope = None
            for scope in reversed(scope_stack):
                if var_name in scope.get("variables", {}):
                    resolved_scope = scope
                    break
            if not resolved_scope:
                print(f"Warning: Identifier '{var_name}' used before declaration.")
            else:
                print(f"Resolved variable '{var_name}' in scope: {resolved_scope}.")

        # recursively process children
        for child in ast.get("children", []):
            extract_symbols(child, global_scope, scope_stack)

    return global_scope

def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('Usage: symbols.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Usage: symbols.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open(inputfile, 'r') as input_file:
        ast = json.load(input_file)

    global_scope = extract_symbols(ast)

    if outputfile:
        with open(outputfile, 'w') as output_file:
            yaml_output = yaml_format(global_scope)
            output_file.write("\n".join(yaml_output))
    else:
        yaml_output = yaml_format(global_scope)
        print("\n".join(yaml_output))

if __name__ == "__main__":
   main(sys.argv[1:])
