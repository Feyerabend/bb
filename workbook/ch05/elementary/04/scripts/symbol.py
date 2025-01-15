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

def extract_symbols(ast, current_scope=None, global_scope=None):
    if global_scope is None:
        global_scope = { }
    if current_scope is None:
        current_scope = global_scope
    
    if isinstance(ast, dict):
        if ast.get("type") == "VAR_DECL":
            var_name = ast.get("value")
            current_scope[var_name] = {"type": "variable"}
        
        elif ast.get("type") == "CONST_DECL":
            const_name = ast.get("value")
            const_value = None
            if ast.get("children"):
                # Assuming the first child contains the value
                const_child = ast["children"][0]
                if const_child.get("type") == "NUMBER":
                    const_value = const_child.get("value")
            current_scope[const_name] = {"type": "constant", "value": const_value}

        elif ast.get("type") == "PROC_DECL":
            proc_name = ast.get("value")
            proc_scope = { }
            current_scope[proc_name] = {"type": "procedure", "scope": proc_scope}

            for child in ast.get("children", []):
                extract_symbols(child, current_scope=proc_scope, global_scope=global_scope)
        
        elif ast.get("type") == "BEGIN" or ast.get("type") == "BLOCK":
            block_scope = { }
            for child in ast.get("children", []):
                extract_symbols(child, current_scope=block_scope, global_scope=global_scope)
        
        elif ast.get("type") == "IDENTIFIER":
            identifier_name = ast.get("value")
            if identifier_name not in current_scope:
                current_scope[identifier_name] = {"type": "variable"}

        for child in ast.get("children", []):
            extract_symbols(child, current_scope=current_scope, global_scope=global_scope)

    return global_scope

def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('symbol.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('usage: symbol.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open(inputfile, 'r') as input_file:
        ast = json.load(input_file)

    global_scope = extract_symbols(ast)

    with open(outputfile, 'w') as output_file:
        yaml_output = yaml_format(global_scope)
        output_file.write("\n".join(yaml_output))

if __name__ == "__main__":
   main(sys.argv[1:])