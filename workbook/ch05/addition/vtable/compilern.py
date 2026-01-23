import re
from typing import List, Dict, Optional
from dataclasses import dataclass

# REDO: TOO CLUTTERYED WITH ASCII ART, AND NO SEPARATING OF CODE FROM EXPLANATION!

TOKENS = [
    ('CLASS', r'\bclass\b'),
    ('INHERITS', r'\binherits\b'),
    ('DEF', r'\bdef\b'),
    ('PRINT', r'\bprint\b'),
    ('THIS', r'\bthis\b'),
    ('STRING', r'"[^"]*"'),
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('SEMI', r';'),
    ('DOT', r'\.'),
    ('SKIP', r'\s+'),
]

def lex(src):
    tokens = []
    pos = 0
    while pos < len(src):
        for tok_type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(src, pos)
            if match:
                if tok_type != 'SKIP':
                    tokens.append((tok_type, match.group(0)))
                pos = match.end()
                break
        else:
            raise SyntaxError(f"Unexpected char: {src[pos]}")
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, tok_type):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] == tok_type

    def consume(self, expected_type):
        if self.peek(expected_type):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        else:
            current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else "EOF"
            raise SyntaxError(f"Expected {expected_type}, got {current_token[0]}")

    def parse_class(self):
        self.consume('CLASS')
        name = self.consume('ID')[1]
        parent = 'Object'
        if self.peek('INHERITS'):
            self.consume('INHERITS')
            parent = self.consume('ID')[1]
        self.consume('LBRACE')
        methods = []
        while not self.peek('RBRACE'):
            if self.peek('DEF'):
                self.consume('DEF')
                methods.append(self.parse_method())
        self.consume('RBRACE')
        return {'name': name, 'parent': parent, 'methods': methods}

    def parse_method(self):
        name = self.consume('ID')[1]
        self.consume('LPAREN')
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while not self.peek('RBRACE'):
            if self.peek('PRINT'):
                self.consume('PRINT')
                body.append(self.parse_print())
        self.consume('RBRACE')
        return {'name': name, 'body': body}

    def parse_print(self):
        self.consume('LPAREN')
        expr = self.consume('STRING')[1]
        self.consume('RPAREN')
        self.consume('SEMI')
        return {'type': 'print', 'value': expr[1:-1]}  # strip quotes


# VTABLE REPRESENTATION

@dataclass
class Method:
    """Represents a method in a class."""
    name: str
    implementation: str  # which class implements this
    overridden_from: Optional[str] = None  # if this overrides a parent method
    
    def __str__(self):
        if self.overridden_from:
            return f"{self.name} → {self.implementation}_{self.name} (overrides {self.overridden_from})"
        return f"{self.name} → {self.implementation}_{self.name}"

@dataclass
class VTable:
    """Represents a virtual method table."""
    class_name: str
    parent: Optional[str]
    methods: List[Method]
    
    def visualize(self) -> str:
        """Create ASCII art visualization of VTable."""
        lines = []
        lines.append(f"┌─ {self.class_name}VTable ─────────────────┐")
        
        if self.parent:
            lines.append(f"│ parent: {self.parent}VTable*        │")
            lines.append("├────────────────────────────────┤")
        
        for method in self.methods:
            override_marker = " ⚡" if method.overridden_from else ""
            lines.append(f"│ {method.name:10} → {method.implementation}_{method.name}{override_marker}")
            lines.append("│" + " " * 31 + "│")
        
        lines.append("└────────────────────────────────┘")
        return "\n".join(lines)


# VTABLE BUILDER

class VTableBuilder:
    """Builds VTables for a class hierarchy."""
    
    def __init__(self):
        self.classes: Dict[str, dict] = {}
        self.vtables: Dict[str, VTable] = {}
        
        # Add base Object class
        self.classes['Object'] = {
            'name': 'Object',
            'parent': None,
            'methods': [{'name': 'destroy', 'body': []}]
        }
    
    def add_class(self, class_def: dict):
        """Add a class definition."""
        self.classes[class_def['name']] = class_def
    
    def build_vtables(self):
        """Build VTables for all classes, respecting inheritance."""
        # Build in dependency order (parents before children)
        for class_name in self._topological_sort():
            self._build_vtable(class_name)
    
    def _topological_sort(self) -> List[str]:
        """Sort classes so parents come before children."""
        visited = set()
        result = []
        
        def visit(name):
            if name in visited:
                return
            visited.add(name)
            
            class_def = self.classes[name]
            parent = class_def.get('parent')
            if parent and parent in self.classes:
                visit(parent)
            
            result.append(name)
        
        for name in self.classes:
            visit(name)
        
        return result
    
    def _build_vtable(self, class_name: str):
        """Build VTable for a specific class."""
        class_def = self.classes[class_name]
        parent_name = class_def.get('parent')
        
        # Start with parent's methods (inheritance!)
        methods = []
        inherited_methods = {}
        
        if parent_name and parent_name in self.vtables:
            parent_vtable = self.vtables[parent_name]
            for method in parent_vtable.methods:
                # Inherit method from parent
                inherited_methods[method.name] = method
                methods.append(Method(
                    name=method.name,
                    implementation=method.implementation,
                    overridden_from=None
                ))
        
        # Add/override with this class's methods
        for method_def in class_def['methods']:
            method_name = method_def['name']
            
            if method_name in inherited_methods:
                # Override parent's method!
                for i, m in enumerate(methods):
                    if m.name == method_name:
                        methods[i] = Method(
                            name=method_name,
                            implementation=class_name,
                            overridden_from=inherited_methods[method_name].implementation
                        )
                        break
            else:
                # New method (not in parent)
                methods.append(Method(
                    name=method_name,
                    implementation=class_name,
                    overridden_from=None
                ))
        
        self.vtables[class_name] = VTable(
            class_name=class_name,
            parent=parent_name,
            methods=methods
        )
    
    def visualize_hierarchy(self) -> str:
        """Show the entire class hierarchy with VTables."""
        lines = []
        
        def show_class(class_name, indent=0):
            if class_name not in self.vtables:
                return
            
            vtable = self.vtables[class_name]
            prefix = "  " * indent
            
            # Show VTable
            vtable_lines = vtable.visualize().split('\n')
            for line in vtable_lines:
                lines.append(prefix + line)
            
            # Show children
            children = [name for name, cls in self.classes.items() 
                       if cls.get('parent') == class_name]
            
            if children:
                lines.append(prefix + "  │")
                lines.append(prefix + "  ├─ inherits ──┐")
                lines.append(prefix + "  │             ↓")
                for child in children:
                    show_class(child, indent + 1)
        
        show_class('Object')
        return '\n'.join(lines)

# ============================================================================
# METHOD DISPATCH SIMULATOR
# ============================================================================

class MethodDispatchSimulator:
    """Simulates dynamic dispatch through VTables."""
    
    def __init__(self, vtables: Dict[str, VTable]):
        self.vtables = vtables
    
    def simulate_call(self, object_type: str, declared_type: str, method_name: str) -> str:
        """
        Simulate a method call showing the dispatch mechanism.
        
        object_type: Actual runtime type of the object
        declared_type: Compile-time type of the variable
        method_name: Name of the method being called
        """
        lines = []
        lines.append(f"SIMULATING: {declared_type}* obj = new {object_type}();")
        lines.append(f"            obj->{method_name}();")
        lines.append("")
        lines.append("Step-by-step dispatch:")
        lines.append("")
        
        # Step 1: Object creation
        lines.append(f"1. Object created with type: {object_type}")
        lines.append(f"   ┌─────────────────┐")
        lines.append(f"   │ {object_type} object   │")
        lines.append(f"   ├─────────────────┤")
        lines.append(f"   │ vtable ────────┐│")
        lines.append(f"   └────────────────│┘")
        lines.append(f"                    ↓")
        lines.append(f"         Points to {object_type}VTable")
        lines.append("")
        
        # Step 2: Method lookup
        vtable = self.vtables[object_type]
        method = None
        for m in vtable.methods:
            if m.name == method_name:
                method = m
                break
        
        if not method:
            lines.append(f"   ERROR: Method '{method_name}' not found!")
            return '\n'.join(lines)
        
        lines.append(f"2. Looking up '{method_name}' in VTable:")
        lines.append(f"   {object_type}VTable contains:")
        for m in vtable.methods:
            if m.name == method_name:
                lines.append(f"   → {m.name}: {m.implementation}_{m.name}  ← FOUND!")
            else:
                lines.append(f"     {m.name}: {m.implementation}_{m.name}")
        lines.append("")
        
        # Step 3: Dispatch
        lines.append(f"3. Dispatch to implementation:")
        if method.overridden_from:
            lines.append(f"   {declared_type}_{method_name} (declared)")
            lines.append(f"          ↓ (overridden!)")
            lines.append(f"   {method.implementation}_{method_name} (actual) ⚡")
        else:
            lines.append(f"   {method.implementation}_{method_name}")
        lines.append("")
        lines.append(f"4. Execute: {method.implementation}_{method_name}()")
        
        return '\n'.join(lines)

# ============================================================================
# C CODE GENERATOR (with detailed comments)
# ============================================================================

def generate_annotated_c_code(ast: dict, vtable_builder: VTableBuilder) -> str:
    """Generate C code with detailed VTable annotations."""
    lines = []
    lines.append('#include <stdio.h>')
    lines.append('#include <stdlib.h>')
    lines.append('')
    lines.append('// ============================================')
    lines.append('// BASE OBJECT')
    lines.append('// ============================================')
    lines.append('')
    lines.append('typedef struct Object {')
    lines.append('    struct ObjectVTable* vtable;  // ← VTABLE POINTER!')
    lines.append('} Object;')
    lines.append('')
    lines.append('typedef struct ObjectVTable {')
    lines.append('    void (*destroy)(Object* self);')
    lines.append('} ObjectVTable;')
    lines.append('')
    lines.append('void object_destroy(Object* self) {')
    lines.append('    free(self);')
    lines.append('}')
    lines.append('')
    lines.append('ObjectVTable object_vtable = {')
    lines.append('    .destroy = object_destroy')
    lines.append('};')
    lines.append('')
    
    class_name = ast['name']
    parent = ast['parent']
    
    lines.append('// ============================================')
    lines.append(f'// {class_name} CLASS')
    lines.append('// ============================================')
    lines.append('')
    lines.append(f'typedef struct {class_name} {{')
    lines.append(f'    {parent} base;  // ← Inheritance via composition')
    lines.append(f'}} {class_name};')
    lines.append('')
    
    lines.append(f'// {class_name} VTABLE STRUCTURE')
    lines.append(f'typedef struct {class_name}VTable {{')
    lines.append(f'    ObjectVTable base;  // ← Inherit base vtable')
    for method in ast['methods']:
        lines.append(f'    void (*{method["name"]})(Object* self);  // ← Method pointer')
    lines.append(f'}} {class_name}VTable;')
    lines.append('')
    
    lines.append('// METHOD IMPLEMENTATIONS')
    for method in ast['methods']:
        lines.append(f'void {class_name}_{method["name"]}(Object* self) {{')
        for stmt in method['body']:
            if stmt['type'] == 'print':
                lines.append(f'    printf("{stmt["value"]}\\n");')
        lines.append('}')
        lines.append('')
    
    lines.append(f'// VTABLE INSTANCE (GLOBAL)')
    lines.append(f'// This is THE vtable - only ONE exists per class!')
    lines.append(f'{class_name}VTable {class_name.lower()}_vtable = {{')
    lines.append('    .base = { .destroy = object_destroy },')
    for method in ast['methods']:
        lines.append(f'    .{method["name"]} = {class_name}_{method["name"]},  // ← Points to implementation')
    lines.append('};')
    lines.append('')
    
    lines.append('// CONSTRUCTOR')
    lines.append(f'{class_name}* {class_name}_create() {{')
    lines.append(f'    {class_name}* self = malloc(sizeof({class_name}));')
    lines.append(f'    self->base.vtable = (ObjectVTable*)&{class_name.lower()}_vtable;  // ← Link to VTable!')
    lines.append('    return self;')
    lines.append('}')
    lines.append('')
    
    lines.append('// MAIN - DEMONSTRATES DISPATCH')
    lines.append('int main() {')
    lines.append(f'    {class_name}* obj = {class_name}_create();')
    lines.append(f'    ')
    lines.append(f'    // Dynamic dispatch through VTable:')
    lines.append(f'    // 1. Load obj->base.vtable')
    lines.append(f'    // 2. Cast to {class_name}VTable*')
    lines.append(f'    // 3. Call vtable->{ast["methods"][0]["name"]}')
    lines.append(f'    (({class_name}VTable*)obj->base.vtable)->{ast["methods"][0]["name"]}((Object*)obj);')
    lines.append(f'    ')
    lines.append('    ((ObjectVTable*)obj->base.vtable)->destroy((Object*)obj);')
    lines.append('    return 0;')
    lines.append('}')
    
    return '\n'.join(lines)




def demo():
    # Example 1: Single class
    print("="*70)
    print("VIRTUAL TABLE (VTABLE) DEMONSTRATION")
    print("="*70)
    
    source1 = """
class Dog inherits Object {
    def bark() {
        print("Woof!");
    }
}
"""
    
    print("\nSource Code:")
    print(source1)
    
    tokens = lex(source1)
    parser = Parser(tokens)
    ast = parser.parse_class()
    
    builder = VTableBuilder()
    builder.add_class(ast)
    builder.build_vtables()
    
    print("\n" + "="*70)
    print("VTABLE STRUCTURE")
    print("="*70)
    print("\nEvery Dog object has a pointer to this ONE shared VTable:\n")
    print(builder.vtables['Dog'].visualize())
    
    print("\n" + "="*70)
    print("KEY CONCEPT: Virtual Tables")
    print("="*70)
    print("""
A VTable (Virtual Table) is a lookup table of function pointers used to
resolve method calls at runtime (dynamic dispatch).

Structure:
  • Each CLASS has ONE vtable (shared by all instances)
  • Each OBJECT has a pointer to its class's vtable
  • Method calls follow: object → vtable → function pointer

Benefits:
  • Enables polymorphism
  • Allows method overriding
  • Runtime dispatch (call correct method based on actual type)
""")
    
    # Example 2: Inheritance with overriding
    print("\n" + "="*70)
    print("INHERITANCE & METHOD OVERRIDING")
    print("="*70)
    
    source2 = """
class Animal inherits Object {
    def speak() {
        print("Some sound");
    }
}
"""
    
    source3 = """
class Cat inherits Animal {
    def speak() {
        print("Meow!");
    }
}
"""
    
    builder2 = VTableBuilder()
    
    tokens2 = lex(source2)
    parser2 = Parser(tokens2)
    ast2 = parser2.parse_class()
    builder2.add_class(ast2)
    
    tokens3 = lex(source3)
    parser3 = Parser(tokens3)
    ast3 = parser3.parse_class()
    builder2.add_class(ast3)
    
    builder2.build_vtables()
    
    print("\nClass Hierarchy with VTables:\n")
    print(builder2.visualize_hierarchy())
    
    print("\n⚡ = Method overridden from parent class")
    print("\nNotice: Cat's VTable has 'speak' pointing to Cat_speak, not Animal_speak!")
    
    # Simulate dispatch
    print("\n" + "="*70)
    print("DYNAMIC DISPATCH SIMULATION")
    print("="*70)
    print("")
    
    simulator = MethodDispatchSimulator(builder2.vtables)
    print(simulator.simulate_call('Cat', 'Animal', 'speak'))
    
    print("\n" + "="*70)
    print("WHY VTABLES MATTER")
    print("="*70)
    print("""
Without VTables (Static Dispatch):
  Animal* a = new Cat();
  a->speak();  // Would call Animal_speak (WRONG!)

With VTables (Dynamic Dispatch):
  Animal* a = new Cat();
  a->speak();  // Follows vtable → calls Cat_speak (CORRECT!)

This is the foundation of polymorphism in C++, Java, Python, etc.
The VTable makes runtime type information available for method calls.
""")
    
    # Show generated C code
    print("\n" + "="*70)
    print("GENERATED C CODE (Annotated)")
    print("="*70)
    print("\nShowing how VTables are implemented in C:\n")
    print(generate_annotated_c_code(ast, builder))

if __name__ == "__main__":
    demo()
