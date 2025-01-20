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

def extract_constants(ast, global_scope=None):
    if global_scope is None:
        global_scope = {"constants": {}}

    if isinstance(ast, dict):
        node_type = ast.get("type")

        if node_type == "CONST_DECL":
            const_name = ast.get("value")
            const_value = None
            if ast.get("children"):
                const_child = ast["children"][0]
                if const_child.get("type") == "NUMBER":
                    const_value = const_child.get("value")
            if const_name:
                global_scope["constants"][const_name] = {"type": "constant", "value": const_value}

        for child in ast.get("children", []):
            extract_constants(child, global_scope)

    return global_scope


##


def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('Usage: constants.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Usage: constants.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open(inputfile, 'r') as input_file:
        ast = json.load(input_file)

    global_scope = extract_constants(ast)

    if outputfile:
        with open(outputfile, 'w') as output_file:
            yaml_output = yaml_format(global_scope["constants"])
            output_file.write("\n".join(yaml_output))
    else:
        yaml_output = yaml_format(global_scope["constants"])
        print("\n".join(yaml_output))

if __name__ == "__main__":
   main(sys.argv[1:])
