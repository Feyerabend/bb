#!/usr/bin/env python3

import os
import sys
import importlib.util
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
import inspect

# Import the core compiler components
try:
    from core import (
        ASTNode, Visitor, CompilerContext, MessageCollector, 
        BlockNode, AssignNode, CallNode, ReadNode, WriteNode,
        CompoundNode, NestedBlockNode, IfNode, WhileNode,
        OperationNode, VariableNode, NumberNode, PL0Compiler
    )
except ImportError:
    print("Error: Cannot import core. Make sure core.py is in the same directory.")
    sys.exit(1)


class Plugin(ABC):
    """Base class for compiler plugins"""
    
    def __init__(self, name: str, description: str = "", version: str = "1.0"):
        self.name = name
        self.description = description
        self.version = version
    
    @abstractmethod
    def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> Any:
        """Execute the plugin and return results"""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Return list of plugin names this plugin depends on"""
        return []


def plugin_function(name: str, description: str = "", dependencies: List[str] = None):
    """Decorator to create function-based plugins"""
    def decorator(func):
        class FunctionPlugin(Plugin):
            def __init__(self):
                super().__init__(name, description)
                self.dependencies = dependencies or []
                self.func = func
            
            def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> Any:
                return self.func(ast, context, messages)
            
            def get_dependencies(self) -> List[str]:
                return self.dependencies
        
        func._plugin_class = FunctionPlugin
        return func
    return decorator


class PluginManager:
    """Manages and executes compiler plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_order: List[str] = []
        self.loaded_files: List[str] = []
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        self._update_execution_order()

    def _update_execution_order(self):
        """Update plugin execution order based on dependencies"""
        visited = set()
        temp_visited = set()
        self.plugin_order = []
        skipped_plugins = []

        def visit(plugin_name):
            if plugin_name in temp_visited:
                self.messages.warning(f"Circular dependency detected involving plugin: {plugin_name}. Skipping plugin.")
                skipped_plugins.append(plugin_name)
                return
            if plugin_name not in visited:
                temp_visited.add(plugin_name)
                plugin = self.plugins.get(plugin_name)
                if plugin:
                    for dep in plugin.get_dependencies():
                        if dep not in self.plugins:
                            self.messages.warning(f"Plugin dependency not found: {dep} for plugin {plugin_name}. Skipping plugin.")
                            skipped_plugins.append(plugin_name)
                            return
                        visit(dep)
                    temp_visited.remove(plugin_name)
                    visited.add(plugin_name)
                    self.plugin_order.append(plugin_name)

        for plugin_name in list(self.plugins.keys()):
            if plugin_name not in visited and plugin_name not in skipped_plugins:
                visit(plugin_name)

        # Remove skipped plugins from self.plugins
        for plugin_name in skipped_plugins:
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
                self.messages.info(f"Removed plugin {plugin_name} due to dependency issues.")

    def load_plugin_file(self, plugin_file: str, messages: MessageCollector):
        """Load plugins from a Python file"""
        self.messages = messages  # Store messages for use in _update_execution_order
        try:
            messages.debug(f"Attempting to load plugin file: {plugin_file}")
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_file)
            if spec is None:
                messages.error(f"Failed to create spec for plugin file: {plugin_file}")
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            plugins_loaded = 0
            
            # Look for Plugin classes
            messages.debug(f"Scanning for class-based plugins in {plugin_file}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                messages.debug(f"Checking attribute: {attr_name}, type: {type(attr)}")
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr != Plugin):
                    messages.debug(f"Found plugin class: {attr_name}")
                    plugin_instance = attr()
                    self.register_plugin(plugin_instance)
                    messages.info(f"Loaded class plugin: {plugin_instance.name}")
                    plugins_loaded += 1
            
            # Look for function-based plugins
            messages.debug(f"Scanning for function-based plugins in {plugin_file}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if inspect.isfunction(attr) and hasattr(attr, '_plugin_class'):
                    messages.debug(f"Found function plugin: {attr_name}")
                    plugin_instance = attr._plugin_class()
                    self.register_plugin(plugin_instance)
                    messages.info(f"Loaded function plugin: {plugin_instance.name}")
                    plugins_loaded += 1
            
            if plugins_loaded > 0:
                self.loaded_files.append(plugin_file)
                messages.info(f"Loaded {plugins_loaded} plugin(s) from {os.path.basename(plugin_file)}")
            else:
                messages.warning(f"No plugins found in {os.path.basename(plugin_file)}")
            
            # Update execution order after loading all plugins
            self._update_execution_order()
            
        except Exception as e:
            messages.error(f"Failed to load plugin file {plugin_file}: {str(e)}")

    
    def list_plugins(self) -> List[Dict[str, str]]:
        """Get list of registered plugins"""
        return [
            {
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "dependencies": plugin.get_dependencies()
            }
            for plugin in self.plugins.values()
        ]
    
    def execute_plugins(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> ASTNode:
        """Execute all plugins in dependency order and return the final AST"""
        current_ast = ast
        for plugin_name in self.plugin_order:
            plugin = self.plugins[plugin_name]
            try:
                messages.info(f"Executing plugin: {plugin_name}")
                result = plugin.execute(current_ast, context, messages)
                context.plugin_results[plugin_name] = result
                # If the plugin returns an ASTNode, update the current AST
                if isinstance(result, ASTNode):
                    current_ast = result
                    messages.info(f"Plugin {plugin_name} modified the AST")
                messages.info(f"Plugin {plugin_name} completed successfully")
            except Exception as e:
                messages.error(f"Plugin {plugin_name} failed: {str(e)}")
                raise
        return current_ast


class PythonCodeGenPlugin(Plugin):
    """Plugin to generate Python code"""
    
    def __init__(self):
        super().__init__(
            "python_codegen",
            "Generates Python code from PL/0 AST",
            "1.0"
        )
    
    def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> str:
        generator = PythonCodeGenerator(context, messages)
        python_code = generator.generate(ast)
        
        if context.base_name:
            filename = f"{context.base_name}.py"
        else:
            filename = "output.py"
        
        output_path = context.get_output_path(filename)
        try:
            with open(output_path, 'w') as f:
                f.write("#!/usr/bin/env python3\n")
                f.write("# Generated by PL/0 Compiler\n\n")
                f.write(python_code)
            
            messages.info(f"Python code generated: {filename}")
        except Exception as e:
            messages.error(f"Failed to write Python code: {e}")
        
        return python_code


class PythonCodeGenerator(Visitor):
    """Generates Python code from AST"""
    
    def __init__(self, context: CompilerContext, messages: MessageCollector):
        self.context = context
        self.messages = messages
        self.code = []
        self.indent_level = 0

    def generate(self, ast: ASTNode) -> str:
        self.code = []
        try:
            ast.accept(self)
            result = '\n'.join(self.code)
            self.messages.debug("Python code generation completed")
            return result
        except Exception as e:
            self.messages.error(f"Python code generation failed: {str(e)}")
            raise

    def _indent(self) -> str:
        return "    " * self.indent_level

    def _emit(self, line: str):
        self.code.append(self._indent() + line)

    def visit_block(self, node: BlockNode):
        self._emit("# Block start")
        
        if node.variables:
            for var_name in node.variables:
                self._emit(f"{var_name} = 0  # Variable declaration")
            self._emit("")
        
        for proc_name, proc_block in node.procedures:
            self._emit(f"def {proc_name}():")
            self.indent_level += 1
            self._emit("global " + ", ".join(node.variables) if node.variables else "pass")
            proc_block.accept(self)
            self.indent_level -= 1
            self._emit("")
        
        node.statement.accept(self)

    def visit_assign(self, node: AssignNode):
        expr_code = self._generate_expression(node.expression)
        self._emit(f"{node.var_name} = {expr_code}")

    def visit_call(self, node: CallNode):
        self._emit(f"{node.proc_name}()")

    def visit_read(self, node: ReadNode):
        self._emit(f"{node.var_name} = int(input('Enter value for {node.var_name}: '))")

    def visit_write(self, node: WriteNode):
        expr_code = self._generate_expression(node.expression)
        self._emit(f"print({expr_code})")

    def visit_compound(self, node: CompoundNode):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_nested_block(self, node: NestedBlockNode):
        self._emit("# Nested block start")
        
        for var_name in node.variables:
            self._emit(f"{var_name} = 0  # Nested variable declaration")
        
        for stmt in node.statements:
            stmt.accept(self)
            
        self._emit("# Nested block end")

    def visit_if(self, node: IfNode):
        condition_code = self._generate_expression(node.condition)
        self._emit(f"if {condition_code}:")
        self.indent_level += 1
        node.then_statement.accept(self)
        self.indent_level -= 1

    def visit_while(self, node: WhileNode):
        condition_code = self._generate_expression(node.condition)
        self._emit(f"while {condition_code}:")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1

    def visit_operation(self, node: OperationNode):
        pass

    def visit_variable(self, node: VariableNode):
        pass

    def visit_number(self, node: NumberNode):
        pass

    def _generate_expression(self, node: ASTNode) -> str:
        if isinstance(node, NumberNode):
            return str(node.value)
        elif isinstance(node, VariableNode):
            return node.name
        elif isinstance(node, OperationNode):
            left = self._generate_expression(node.left)
            right = self._generate_expression(node.right)
            if node.operator == "=":
                return f"({left} == {right})"
            else:
                return f"({left} {node.operator} {right})"
        else:
            raise ValueError(f"Unknown expression node type: {type(node)}")


class StaticAnalysisPlugin(Plugin):
    """Plugin for static analysis"""
    
    def __init__(self):
        super().__init__(
            "static_analysis",
            "Performs static analysis on PL/0 programs",
            "1.0"
        )
    
    def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> Dict[str, Any]:
        analyzer = StaticAnalyzer()
        results = analyzer.analyze(ast)
        
        if context.base_name:
            report_path = context.get_output_path(f"{context.base_name}_static_analysis.txt")
            self._write_analysis_report(results, report_path, messages)
        
        messages.info(f"Static analysis found {len(results['declared_variables'])} variables, {len(results['procedures'])} procedures")
        return results
    
    def _write_analysis_report(self, results: Dict[str, Any], filepath: str, messages: MessageCollector):
        try:
            with open(filepath, 'w') as f:
                f.write("Static Analysis Report\n")
                f.write("=" * 21 + "\n\n")
                
                f.write(f"Variables declared: {len(results['declared_variables'])}\n")
                if results['declared_variables']:
                    f.write(f"  Variables: {', '.join(results['declared_variables'])}\n")
                f.write(f"\nVariables used: {len(results['used_variables'])}\n")
                if results['used_variables']:
                    f.write(f"  Used: {', '.join(results['used_variables'])}\n")
                
                unused = set(results['declared_variables']) - set(results['used_variables'])
                if unused:
                    f.write(f"\nUnused variables: {', '.join(unused)}\n")
                
                f.write(f"\nProcedures defined: {len(results['procedures'])}\n")
                if results['procedures']:
                    f.write(f"  Procedures: {', '.join(results['procedures'])}\n")
                
                f.write(f"\nProcedures called: {len(results['called_procedures'])}\n")
                if results['called_procedures']:
                    f.write(f"  Called: {', '.join(results['called_procedures'])}\n")
                
                uncalled = set(results['procedures']) - set(results['called_procedures'])
                if uncalled:
                    f.write(f"\nUncalled procedures: {', '.join(uncalled)}\n")
                
                f.write(f"\nStatement counts:\n")
                f.write(f"  Assignments: {results['statement_counts']['assignments']}\n")
                f.write(f"  Procedure calls: {results['statement_counts']['calls']}\n")
                f.write(f"  Read statements: {results['statement_counts']['reads']}\n")
                f.write(f"  Write statements: {results['statement_counts']['writes']}\n")
                f.write(f"  If statements: {results['statement_counts']['ifs']}\n")
                f.write(f"  While loops: {results['statement_counts']['whiles']}\n")
            
            messages.info(f"Static analysis report saved: {os.path.basename(filepath)}")
        except Exception as e:
            messages.error(f"Failed to write static analysis report: {e}")


class StaticAnalyzer(Visitor):
    """Performs static analysis on AST"""
    
    def __init__(self):
        self.declared_variables = set()
        self.used_variables = set()
        self.procedures = set()
        self.called_procedures = set()
        self.statement_counts = {
            'assignments': 0,
            'calls': 0,
            'reads': 0,
            'writes': 0,
            'ifs': 0,
            'whiles': 0
        }
    
    def analyze(self, ast: ASTNode) -> Dict[str, Any]:
        ast.accept(self)
        return {
            'declared_variables': sorted(list(self.declared_variables)),
            'used_variables': sorted(list(self.used_variables)),
            'procedures': sorted(list(self.procedures)),
            'called_procedures': sorted(list(self.called_procedures)),
            'statement_counts': self.statement_counts
        }
    
    def visit_block(self, node: BlockNode):
        for var in node.variables:
            self.declared_variables.add(var)
        
        for proc_name, proc_block in node.procedures:
            self.procedures.add(proc_name)
            proc_block.accept(self)
        
        node.statement.accept(self)
    
    def visit_assign(self, node: AssignNode):
        self.statement_counts['assignments'] += 1
        self.used_variables.add(node.var_name)
        node.expression.accept(self)
    
    def visit_call(self, node: CallNode):
        self.statement_counts['calls'] += 1
        self.called_procedures.add(node.proc_name)
    
    def visit_read(self, node: ReadNode):
        self.statement_counts['reads'] += 1
        self.used_variables.add(node.var_name)
    
    def visit_write(self, node: WriteNode):
        self.statement_counts['writes'] += 1
        node.expression.accept(self)
    
    def visit_compound(self, node: CompoundNode):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node: NestedBlockNode):
        for var in node.variables:
            self.declared_variables.add(var)
        
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_if(self, node: IfNode):
        self.statement_counts['ifs'] += 1
        node.condition.accept(self)
        node.then_statement.accept(self)
    
    def visit_while(self, node: WhileNode):
        self.statement_counts['whiles'] += 1
        node.condition.accept(self)
        node.body.accept(self)
    
    def visit_operation(self, node: OperationNode):
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node: VariableNode):
        self.used_variables.add(node.name)
    
    def visit_number(self, node: NumberNode):
        pass


class PL0PluginCompiler:
    """Main compiler with plugin system"""
    
    def __init__(self, output_dir: str = None):
        self.core_compiler = PL0Compiler(output_dir)
        self.plugin_manager = PluginManager()
        self._register_builtin_plugins()
    
    def _register_builtin_plugins(self):
        """Register built-in plugins"""
        self.plugin_manager.register_plugin(StaticAnalysisPlugin())
        self.plugin_manager.register_plugin(PythonCodeGenPlugin())
    
    def load_plugin_file(self, plugin_file: str):
        """Load plugins from a file"""
        self.plugin_manager.load_plugin_file(plugin_file, self.core_compiler.messages)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all registered plugins"""
        return self.plugin_manager.list_plugins()
    
    def compile_file(self, filename: str, debug: bool = False) -> bool:
        """Compile a file with all plugins"""
        success, ast = self.core_compiler.compile_file(filename, debug)
        if not success:
            return False
        
        try:
            self.plugin_manager.execute_plugins(ast, self.core_compiler.get_context(), self.core_compiler.messages)
            self.core_compiler.messages.info("All plugins completed successfully!")
            return True
        except Exception as e:
            self.core_compiler.messages.error(f"Plugin execution failed: {str(e)}")
            return False
    
    def get_messages(self):
        """Get all compiler messages"""
        return self.core_compiler.get_messages()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PL/0 Compiler with Plugin System')
    parser.add_argument('input_file', help='PL/0 source file to compile')
    parser.add_argument('-o', '--output-dir', help='Output directory for generated files', default='.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--plugin', action='append', help='Load additional plugin from file')
    parser.add_argument('--list-plugins', action='store_true', help='List available plugins')
    
    args = parser.parse_args()
    
    compiler = PL0PluginCompiler(args.output_dir)
    
    # Load additional plugins before listing or compiling
    if args.plugin:
        for plugin_file in args.plugin:
            compiler.load_plugin_file(plugin_file)
    
    # List plugins if requested
    if args.list_plugins:
        plugins = compiler.list_plugins()
        print("\nAvailable plugins:")
        for plugin in plugins:
            deps = ", ".join(plugin['dependencies']) if plugin['dependencies'] else "none"
            print(f"  {plugin['name']} (v{plugin['version']})")
            print(f"    Description: {plugin['description']}")
            print(f"    Dependencies: {deps}")
        print()
        sys.exit(0)  # Exit after listing plugins
    
    # Proceed with compilation
    success = compiler.compile_file(args.input_file, args.debug)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

