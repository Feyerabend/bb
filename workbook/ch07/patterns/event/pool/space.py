# remove_first_space.py

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            parts = line.split(' ', 1)
            if len(parts) == 2:
                outfile.write(parts[1])
            else:
                outfile.write(line)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python remove_first_space.py input.txt output.txt")
    else:
        process_file(sys.argv[1], sys.argv[2])