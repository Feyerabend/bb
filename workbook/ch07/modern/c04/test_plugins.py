#!/usr/bin/env python3
"""
Demo script showing all compiler outputs including plugin results
"""

import sys
import os

# Add the directory containing compiler.py to Python path
sys.path.append('.')

from compiler import PL0Compiler

def demo_compilation():
    # Sample PL/0 program with some optimization opportunities
    sample_code = """
    var x, y, result;
    begin
        x := 5;
        y := 0;
        result := x + 0;
        result := result * 1;
        if 1 = 1 then
            ! result;
        while 0 = 1 do
            x := x + 1
    end.
    """
    
    print("=== PL/0 Compiler Demo with All Plugin Outputs ===\n")
    print("Source Code:")
    print("-" * 40)
    print(sample_code)
    print("-" * 40)
    
    # Create compiler instance
    compiler = PL0Compiler()
    compiler.enable_debug()
    
    # Load plugins from the plugins directory
    compiler.load_plugins("plugins/")
    
    # Compile the code
    result = compiler.compile_string(sample_code)
    
    print(f"\nCompilation {'SUCCESS' if result['success'] else 'FAILED'}")
    print("=" * 50)
    
    if result["success"]:
        # Show all generated outputs
        print("\n📄 GENERATED OUTPUTS:")
        print("=" * 30)
        
        outputs = result["outputs"]
        for name, content in outputs.items():
            print(f"\n--- {name.upper().replace('_', ' ')} ---")
            print(content[:500] + ("..." if len(content) > 500 else ""))
        
        # Show plugin results
        print("\n🔧 PLUGIN RESULTS:")
        print("=" * 30)
        
        plugin_results = result["plugin_results"]
        for plugin_name, plugin_result in plugin_results.items():
            print(f"\n{plugin_name}:")
            if isinstance(plugin_result, dict):
                for key, value in plugin_result.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {plugin_result}")
    
    # Show messages
    print(f"\n📋 COMPILATION MESSAGES:")
    print("=" * 30)
    for msg in result["messages"]:
        print(f"[{msg.level.value}] {msg.message}")
    
    return result

def write_all_outputs(result, base_filename="demo"):
    """Write all generated outputs to separate files"""
    if not result["success"]:
        return
    
    outputs = result["outputs"]
    files_written = []
    
    # Write each output to a file
    for output_name, content in outputs.items():
        if output_name == "c_code":
            filename = f"{base_filename}.c"
        elif output_name == "tac_code":
            filename = f"{base_filename}.tac"
        elif output_name == "documentation":
            filename = f"{base_filename}.md"
        elif output_name == "ast_structure":
            filename = f"{base_filename}_ast.txt"
        elif output_name == "optimization_hints":
            filename = f"{base_filename}_hints.txt"
        elif output_name == "variable_report":
            filename = f"{base_filename}_variables.txt"
        elif output_name == "statement_report":
            filename = f"{base_filename}_statements.txt"
        else:
            filename = f"{base_filename}_{output_name}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            files_written.append(filename)
            print(f"✅ Wrote {filename}")
        except IOError as e:
            print(f"❌ Failed to write {filename}: {e}")
    
    return files_written

def create_optimization_test():
    """Create a test program with many optimization opportunities"""
    return """
    var a, b, c, unused_var;
    begin
        a := 10 + 0;     // Should optimize to: a := 10
        b := a * 1;      // Should optimize to: b := a
        c := b - 0;      // Should optimize to: c := b
        
        if 1 = 1 then   // Always true condition
            ! c;
            
        if 0 = 1 then   // Always false condition (dead code)
            a := 999;
            
        while 0 < 1 do  // This would run forever, but condition is constant
            begin
                a := a + 1;
                if a > 100 then
                    a := 0
            end
    end.
    """

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--optimization-test":
        print("Running optimization test...")
        compiler = PL0Compiler()
        compiler.enable_debug()
        compiler.load_plugins("plugins/")
        
        test_code = create_optimization_test()
        result = compiler.compile_string(test_code)
        
        if result["success"]:
            write_all_outputs(result, "optimization_test")
    else:
        result = demo_compilation()
        if result["success"]:
            print(f"\n📁 Writing all outputs to files...")
            write_all_outputs(result)
            print("\n✨ Demo complete! Check the generated files.")
