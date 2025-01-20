
import json

class SimpleYamlParser:
    def __init__(self):
        self.symbol_table = {}

    def parse(self, file_path):
        """
        Parse a YAML file and populate the symbol table.

        Args:
            file_path (str): Path to the YAML file.

        Returns:
            dict: The parsed symbol table.
        """
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
            return self._parse_lines(lines)
        except FileNotFoundError:
            raise Exception(f"YAML file '{file_path}' not found.")
        except Exception as e:
            raise Exception(f"Error parsing YAML file: {e}")

    def _parse_lines(self, lines):
        """
        Convert lines of a YAML file into a structured dictionary.

        Args:
            lines (list): List of lines from the YAML file.

        Returns:
            dict: Parsed YAML data.
        """
        data = {}
        stack = [(data, -1)]  # Stack of (current_dict, indent_level)

        for line in lines:
            line = line.rstrip()
            if not line or line.startswith("#"):  # Skip empty lines or comments
                continue

            indent_level = (len(line) - len(line.lstrip())) // 2
            key, value = self._parse_line(line)

            # Find the correct parent based on indentation
            while stack and stack[-1][1] >= indent_level:
                stack.pop()

            current_dict = stack[-1][0] if stack else data
            if value is None:
                # Create a nested dictionary for this key
                current_dict[key] = {}
                stack.append((current_dict[key], indent_level))
            else:
                # Assign the value directly
                current_dict[key] = value

        return data

    def _parse_line(self, line):
        """
        Parse a single YAML line into a key-value pair.

        Args:
            line (str): A single line of YAML.

        Returns:
            tuple: (key, value) pair, where value can be None for nested objects.
        """
        if ":" not in line:
            raise Exception(f"Invalid YAML line: '{line}'")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip() if value.strip() else None
        return key, value

def main():
    yaml_file_path = "sample.symbol"

    try:
        parser = SimpleYamlParser()
        symbol_table = parser.parse(yaml_file_path)

        formatted_output = json.dumps(symbol_table, indent=4)
        print("Parsed Symbol Table:")
        print(formatted_output)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
