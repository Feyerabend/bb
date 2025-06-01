from typing import List, Dict, Any, Optional, Tuple
from jvm_interpreter.parser.class_file_parser import parse_class_file
from jvm_interpreter.models.class_file_models import ClassFile, CodeAttribute

class ClassLoader:
    def __init__(self, class_path: List[str]):
        self.class_path = class_path
        self.loaded_classes: Dict[str, ClassFile] = {}
        self.static_fields: Dict[str, Any] = {}

    def load_class(self, class_name: str) -> ClassFile:
        class_name = class_name.replace('.', '/')
        if class_name in self.loaded_classes:
            return self.loaded_classes[class_name]
        
        for path in self.class_path:
            try:
                file_path = f"{path}/{class_name}.class"
                class_file = parse_class_file(file_path)
                self.loaded_classes[class_name] = class_file
                return class_file
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error loading class {class_name} from {file_path}: {e}")
        
        raise ValueError(f"Class {class_name} not found in class path: {self.class_path}")

    def get_method_code(self, class_name: str, method_name: str) -> Optional[Tuple[int, int, bytes]]:
        class_file = self.load_class(class_name)
        for m in class_file.methods:
            if m.name == method_name:
                for a in m.attributes:
                    if isinstance(a, CodeAttribute):
                        return (a.max_stack, a.max_locals, a.code)
        return None

    def resolve_field(self, class_name: str, field_name: str) -> Any:
        key = f"{class_name}.{field_name}"
        return self.static_fields.get(key)

    def set_field(self, class_name: str, field_name: str, value: Any):
        key = f"{class_name}.{field_name}"
        self.static_fields[key] = value