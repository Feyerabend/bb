#!/bin/bash

# Find all .c and .py files in the current directory
find . -maxdepth 1 -type f \( -name "*.c" -o -name "*.py" \) | sort > list.txt

# Print a message indicating completion
echo "List of .c and .py files saved to list.txt"

