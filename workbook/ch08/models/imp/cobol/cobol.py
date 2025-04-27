def interpret_cobol(code):
    lines = code.strip().split('\n')
    variables = {}
    output = []

    # DATA DIVISION to init variables
    in_data_div = False
    in_working_storage = False
    for line in lines:
        line = line.strip().upper()
        if line.startswith('DATA DIVISION'):
            in_data_div = True
        elif in_data_div and line.startswith('WORKING-STORAGE SECTION'):
            in_working_storage = True
        elif in_working_storage:
            if line.startswith('PROCEDURE DIVISION'):
                break
            if line.startswith('01 '):
                parts = [p.rstrip('.') for p in line.split()]
                if len(parts) >= 2:
                    var_name = parts[1]
                    pic_clause = None
                    try:
                        pic_index = parts.index('PIC')
                        if pic_index + 1 < len(parts):
                            pic_clause = parts[pic_index + 1]
                    except ValueError:
                        pass
                    if pic_clause:
                        if pic_clause.startswith('9'):
                            variables[var_name] = 0
                        elif pic_clause.startswith('X'):
                            length = 1
                            if '(' in pic_clause:
                                length_part = pic_clause.split('(')[1].split(')')[0]
                                try:
                                    length = int(length_part)
                                except ValueError:
                                    pass
                            variables[var_name] = ' ' * length
                        else:
                            variables[var_name] = 0
                    else:
                        variables[var_name] = 0

    # PROCEDURE DIVISION
    in_procedure = False
    for line in lines:
        line = line.strip().upper()
        if line.startswith('PROCEDURE DIVISION'):
            in_procedure = True
            continue
        if not in_procedure:
            continue
        if not line or line.startswith('*'):
            continue
        line = line.split('.', 1)[0].strip()
        if not line:
            continue

        if line.startswith('DISPLAY '):
            content_part = line[8:].strip()
            content = content_part.strip("'\"")
            if content in variables:
                output.append(str(variables[content]))
            else:
                try:
                    output.append(str(int(content)))
                except ValueError:
                    output.append(content)

        elif line.startswith('MOVE '):
            parts = line[5:].split(' TO ', 1)
            if len(parts) == 2:
                value_part, var_part = parts
                value_part = value_part.strip().strip("'\"")
                var_name = var_part.strip()
                try:
                    value = int(value_part)
                except ValueError:
                    value = variables.get(value_part, 0)
                variables[var_name] = value

        elif line.startswith('ADD '):
            parts = line[4:].split(' TO ', 1)
            if len(parts) == 2:
                value_part, var_name = parts
                value_part = value_part.strip()
                var_name = var_name.strip()
                try:
                    value = int(value_part)
                except ValueError:
                    value = variables.get(value_part, 0)
                variables[var_name] = variables.get(var_name, 0) + value

        elif line.startswith('SUBTRACT '):
            parts = line[9:].split(' FROM ', 1)
            if len(parts) == 2:
                value_part, var_name = parts
                value_part = value_part.strip()
                var_name = var_name.strip()
                try:
                    value = int(value_part)
                except ValueError:
                    value = variables.get(value_part, 0)
                variables[var_name] = variables.get(var_name, 0) - value

        elif line == 'STOP RUN':
            break

    return '\n'.join(output)


if __name__ == "__main__":
    sample_code = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SAMPLE.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  NUM             PIC 9(4).
       PROCEDURE DIVISION.
           DISPLAY 'HELLO, WORLD'.
           MOVE 42 TO NUM.
           DISPLAY NUM.
           ADD 8 TO NUM.
           DISPLAY NUM.
           SUBTRACT 10 FROM NUM.
           DISPLAY NUM.
           STOP RUN.
    """
    result = interpret_cobol(sample_code)
    print(result)