import sys

def generate_c_code(ast):
    c_code = [
        '#include <stdio.h>\n',
        '#include <stdlib.h>\n\n',

        'typedef struct Object {\n',
        '    struct ObjectVTable* vtable;\n',
        '} Object;\n\n',

        'typedef struct ObjectVTable {\n',
        '    void (*destroy)(Object* self);\n',
        '} ObjectVTable;\n\n',

        'void object_destroy(Object* self) {\n',
        '    printf("Object destroy: %p\\n", (void*)self);\n',
        '    if (self) free(self);\n',
        '}\n\n',
        'ObjectVTable object_vtable = { .destroy = object_destroy };\n\n'
    ]
    class_registry = {cls['name']: cls for cls in ast['classes']}
    class_registry['Object'] = {'methods': []}

    for cls in ast['classes']:
        class_name = cls['name']
        parent = cls.get('parent', 'Object')
        
        # class struct
        c_code.append(f'typedef struct {class_name} {{\n')
        c_code.append(f'    {parent} base;\n')
        c_code.append(f'}} {class_name};\n\n')

        # VTable struct
        c_code.append(f'typedef struct {class_name}VTable {{\n')
        if parent == 'Object':
            c_code.append('    ObjectVTable* base;\n')
        else:
            c_code.append(f'    {parent}VTable* base;\n')
        c_code.append(f'    void (*destroy)(Object* self);\n')
        for method in cls['methods']:
            c_code.append(f'    void (*{method["name"]})(Object* self);\n')
        c_code.append(f'}} {class_name}VTable;\n\n')

        # method implementations
        for method in cls['methods']:
            c_code.append(f'void {class_name}_{method["name"]}(Object* self) {{\n')
            for stmt in method['body']:
                if stmt['type'] == 'print':
                    c_code.append(f'    printf({stmt["value"]});\n')
            c_code.append('}\n\n')

        # destructor implementation
        c_code.append(f'void {class_name}_destroy(Object* self) {{\n')
        c_code.append(f'    if (!self) return;\n')
        c_code.append(f'    printf("{class_name} destroy: %p, vtable: %p\\n", (void*)self, (void*)self->vtable);\n')
        if parent == 'Object':
            c_code.append(f'    object_destroy(self);\n')
        else:
            c_code.append(f'    {parent}_destroy(self);\n')  # direct parent call
        c_code.append('}\n\n')

        # VTable init
        c_code.append(f'static {class_name}VTable {class_name.lower()}_vtable = {{\n')
        if parent != 'Object':
            c_code.append(f'    .base = &{parent.lower()}_vtable,\n')
        else:
            c_code.append('    .base = &object_vtable,\n')
        c_code.append(f'    .destroy = {class_name}_destroy,\n')
        for method in cls['methods']:
            c_code.append(f'    .{method["name"]} = {class_name}_{method["name"]},\n')
        c_code.append('};\n\n')

        # constructor
        c_code.append(f'{class_name}* {class_name}_create() {{\n')
        c_code.append(f'    {class_name}* self = malloc(sizeof({class_name}));\n')
        c_code.append(f'    if (!self) {{ printf("Memory allocation failed\\n"); exit(1); }}\n')
        c_code.append(f'    printf("{class_name} created: %p\\n", (void*)self);\n')
        if parent == 'Object':
            c_code.append(f'    self->base.vtable = (ObjectVTable*)&{class_name.lower()}_vtable;\n')
        else:
            c_code.append(f'    self->base.base.vtable = (ObjectVTable*)&{class_name.lower()}_vtable;\n')
        c_code.append('    return self;\n}\n\n')

    # generate main()
    c_code.append('int main() {\n')
    created_objects = []
    for stmt in ast['statements']:
        if stmt['type'] == 'assignment':
            c_code.append(f'    {stmt["var_type"]}* {stmt["var_name"]} = ')
            c_code.append(f'({stmt["var_type"]}*){stmt["class"]}_create();\n')
            created_objects.append(stmt['var_name'])
        elif stmt['type'] == 'method_call':
            var_type = next(s['var_type'] for s in ast['statements'] if s.get('var_name') == stmt['object'])
            c_code.append(f'    if ({stmt["object"]}) (({var_type}VTable*){stmt["object"]}->base.vtable)->{stmt["method"]}((Object*){stmt["object"]});\n')
    for obj in created_objects:
        var_type = next(s['var_type'] for s in ast['statements'] if s.get('var_name') == obj)
        c_code.append(f'    if ({obj}) {{ printf("Destroying %s: %p\\n", "{obj}", (void*){obj}); (({var_type}VTable*){obj}->base.vtable)->destroy((Object*){obj}); }}\n')
    c_code.append('    return 0;\n}\n')
    
    return ''.join(c_code)


def main():
  
    # sample
    ast = {
        'classes': [
            {
                'name': 'Animal',
                'parent': 'Object',
                'methods': [
                    {
                        'name': 'speak',
                        'body': [
                            {'type': 'print', 'value': '"Animal sound\\n"'}
                        ]
                    }
                ]
            },
            {
                'name': 'Dog',
                'parent': 'Animal',
                'methods': [
                    {
                        'name': 'speak',
                        'body': [
                            {'type': 'print', 'value': '"Woof!\\n"'}
                        ]
                    }
                ]
            }
        ],
        'statements': [
            {'type': 'assignment', 'var_type': 'Animal', 'var_name': 'animal', 'class': 'Dog'},
            {'type': 'method_call', 'object': 'animal', 'method': 'speak'}
        ]
    }

    c_code = generate_c_code(ast)
    with open("output.c", 'w') as f:
        f.write(c_code)
    print("Generated output.c successfully.")
    print("Compile: gcc -g output.c -o animal")
    print("Run: ./animal")

if __name__ == "__main__":
    main()