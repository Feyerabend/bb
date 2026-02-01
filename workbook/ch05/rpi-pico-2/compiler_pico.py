#!/usr/bin/env python3

import sys
import os
from lexer import tokenize
from parser import Parser
from semantic import SemanticAnalyzer
from codegen import CodeGenerator
from codegen_pico import PicoCodeGenerator
from vm import VirtualMachine

def compile_to_vm(source_code, verbose=False):
    """Compile and run on the virtual machine"""
    try:
        # Lexical analysis
        if verbose:
            print("=== LEXICAL ANALYSIS ===")
        tokens = tokenize(source_code)
        if verbose:
            for token in tokens:
                print(f"  {token}")
            print()
        
        # Syntax analysis
        if verbose:
            print("=== SYNTAX ANALYSIS ===")
        parser = Parser(tokens)
        ast = parser.parse()
        if verbose:
            print(f"  {ast}")
            print()
        
        # Semantic analysis
        if verbose:
            print("=== SEMANTIC ANALYSIS ===")
        analyzer = SemanticAnalyzer(ast)
        errors = analyzer.analyze()
        if errors:
            print("Semantic errors found:")
            for error in errors:
                print(f"  - {error}")
            return False
        if verbose:
            print("  No errors found")
            print()
        
        # Code generation
        if verbose:
            print("=== CODE GENERATION ===")
        generator = CodeGenerator(ast)
        instructions = generator.generate()
        if verbose:
            for i, instr in enumerate(instructions):
                print(f"  {i:3}: {instr}")
            print()
        
        # Execution
        if verbose:
            print("=== EXECUTION ===")
        vm = VirtualMachine()
        vm.load(instructions)
        vm.run()
        
        if verbose:
            print()
            print("=== FINAL MEMORY STATE ===")
            for var, value in vm.memory.items():
                print(f"  {var} = {value}")
        
        return True
    
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return False
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def compile_to_pico(source_code, output_file, verbose=False):
    """Compile to C code for Raspberry Pi Pico 2"""
    try:
        # Lexical analysis
        if verbose:
            print("=== LEXICAL ANALYSIS ===")
        tokens = tokenize(source_code)
        if verbose:
            for token in tokens:
                print(f"  {token}")
            print()
        
        # Syntax analysis
        if verbose:
            print("=== SYNTAX ANALYSIS ===")
        parser = Parser(tokens)
        ast = parser.parse()
        if verbose:
            print(f"  {ast}")
            print()
        
        # Semantic analysis
        if verbose:
            print("=== SEMANTIC ANALYSIS ===")
        analyzer = SemanticAnalyzer(ast)
        errors = analyzer.analyze()
        if errors:
            print("Semantic errors found:")
            for error in errors:
                print(f"  - {error}")
            return False
        if verbose:
            print("  No errors found")
            print()
        
        # Code generation for Pico
        if verbose:
            print("=== CODE GENERATION (Pico C) ===")
        generator = PicoCodeGenerator(ast)
        c_code = generator.generate()
        
        # Write to output file
        with open(output_file, 'w') as f:
            f.write(c_code)
        
        if verbose:
            print(f"  Generated C code written to: {output_file}")
            print()
        
        print(f"Successfully generated C code for Raspberry Pi Pico 2: {output_file}")
        print("To compile:")
        print(f"  1. Copy {output_file} and display.h/display.c to your Pico SDK project")
        print(f"  2. Update CMakeLists.txt to include the display library")
        print(f"  3. Build with: mkdir build && cd build && cmake .. && make")
        
        return True
    
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python compiler_pico.py <source_file> [options]")
        print()
        print("Options:")
        print("  --target vm       Run on virtual machine (default)")
        print("  --target pico     Generate C code for Raspberry Pi Pico 2")
        print("  --output <file>   Output file for generated code (default: output.c)")
        print("  --verbose, -v     Verbose output")
        print()
        print("Examples:")
        print("  python compiler_pico.py program.txt")
        print("  python compiler_pico.py program.txt --target pico --output program.c")
        sys.exit(1)
    
    filename = sys.argv[1]
    target = "vm"
    output_file = "output.c"
    verbose = False
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--target":
            if i + 1 < len(sys.argv):
                target = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --target requires an argument")
                sys.exit(1)
        elif arg == "--output":
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --output requires an argument")
                sys.exit(1)
        elif arg in ("--verbose", "-v"):
            verbose = True
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            sys.exit(1)
    
    # Read source file
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    # Compile based on target
    if target == "vm":
        success = compile_to_vm(source_code, verbose)
    elif target == "pico":
        success = compile_to_pico(source_code, output_file, verbose)
    else:
        print(f"Error: Unknown target '{target}'. Use 'vm' or 'pico'")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
