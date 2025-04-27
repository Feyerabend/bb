
def interpret_cobol(code):
    lines = code.strip().split('\n')
    variables = {}
    output = []

    for line in lines:
        line = line.strip().upper()
        if not line or line.startswith('*'):
            continue


        if line.startswith('DISPLAY '):
            content = line[8:].strip().strip('"\'')
            if content in variables:
                output.append(str(variables[content]))
            else:
                output.append(content)


        elif line.startswith('MOVE '):
            parts = line[5:].split(' TO ')
            if len(parts) == 2:
                value = parts[0].strip().strip('"\'')
                var_name = parts[1].strip()
                try:
                    variables[var_name] = int(value)
                except ValueError:
                    variables[var_name] = value


        elif line.startswith('ADD '):
            parts = line[4:].split(' TO ')
            if len(parts) == 2:
                value = parts[0].strip()
                var_name = parts[1].strip()
                try:
                    num = int(value) if value not in variables else variables[value]
                    variables[var_name] = variables.get(var_name, 0) + num
                except (ValueError, TypeError):
                    output.append("Error: Invalid ADD operation")


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
