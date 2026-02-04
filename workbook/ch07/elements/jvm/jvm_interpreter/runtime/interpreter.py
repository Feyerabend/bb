import struct
#import importlib
from typing import List, Dict, Any, Optional
from jvm_interpreter.models.class_file_models import ConstantPoolEntry, CodeAttribute
from jvm_interpreter.runtime.class_loader import ClassLoader

class Interpreter:
    def __init__(self, code: bytes, max_stack: int, max_locals: int, cp: List[ConstantPoolEntry], class_loader: ClassLoader):
        self.code = list(code)
        self.max_stack = max_stack
        self.max_locals = max_locals
        self.constant_pool = cp
        self.class_loader = class_loader
        self.pc = 0
        self.stack: List[Any] = []
        self.locals: List[Any] = [None] * max_locals
        self.fields: Dict[str, Any] = {}
        self.instructions = {
            1: self.instr_aconst_null,
            2: self.instr_iconst,
            3: self.instr_iconst,
            4: self.instr_iconst,
            5: self.instr_iconst,
            6: self.instr_iconst,
            7: self.instr_iconst,
            8: self.instr_iconst,
            9: self.instr_lconst,
            10: self.instr_lconst,
            11: self.instr_fconst,
            12: self.instr_fconst,
            13: self.instr_fconst,
            14: self.instr_dconst,
            15: self.instr_dconst,
            16: self.instr_bipush,
            17: self.instr_sipush,
            18: self.instr_ldc,
            19: self.instr_ldc_w,
            21: self.instr_iload,
            22: self.instr_lload,
            23: self.instr_fload,
            24: self.instr_dload,
            25: self.instr_aload,
            26: self.instr_iload_n,
            27: self.instr_iload_n,
            28: self.instr_iload_n,
            29: self.instr_iload_n,
            30: self.instr_lload_n,
            31: self.instr_lload_n,
            32: self.instr_lload_n,
            33: self.instr_lload_n,
            34: self.instr_fload_n,
            35: self.instr_fload_n,
            36: self.instr_fload_n,
            37: self.instr_fload_n,
            38: self.instr_dload_n,
            39: self.instr_dload_n,
            40: self.instr_dload_n,
            41: self.instr_dload_n,
            42: self.instr_aload_n,
            43: self.instr_aload_n,
            44: self.instr_aload_n,
            45: self.instr_aload_n,
            54: self.instr_istore,
            55: self.instr_lstore,
            56: self.instr_fstore,
            57: self.instr_dstore,
            58: self.instr_astore,
            59: self.instr_istore_n,
            60: self.instr_istore_n,
            61: self.instr_istore_n,
            62: self.instr_istore_n,
            63: self.instr_lstore_n,
            64: self.instr_lstore_n,
            65: self.instr_lstore_n,
            66: self.instr_lstore_n,
            67: self.instr_fstore_n,
            68: self.instr_fstore_n,
            69: self.instr_fstore_n,
            70: self.instr_fstore_n,
            71: self.instr_dstore_n,
            72: self.instr_dstore_n,
            73: self.instr_dstore_n,
            74: self.instr_dstore_n,
            75: self.instr_astore_n,
            76: self.instr_astore_n,
            77: self.instr_astore_n,
            78: self.instr_astore_n,
            87: self.instr_pop,
            88: self.instr_pop2,
            89: self.instr_dup,
            96: self.instr_iadd,
            100: self.instr_isub,
            104: self.instr_imul,
            108: self.instr_idiv,
            112: self.instr_irem,
            153: self.instr_ifeq,
            154: self.instr_ifne,
            155: self.instr_iflt,
            156: self.instr_ifge,
            157: self.instr_ifgt,
            158: self.instr_ifle,
            159: self.instr_if_icmpeq,
            160: self.instr_if_icmpne,
            161: self.instr_if_icmplt,
            162: self.instr_if_icmpge,
            163: self.instr_if_icmpgt,
            164: self.instr_if_icmple,
            167: self.instr_goto,
            172: self.instr_ireturn,
            177: self.instr_return,
            178: self.instr_getstatic,
            179: self.instr_putstatic,
            180: self.instr_getfield,
            181: self.instr_putfield,
            182: self.instr_invokevirtual,
            183: self.instr_invokespecial,
            184: self.instr_invokestatic,
            185: self.instr_invokeinterface
        }

    def advance(self, n: int = 1) -> int:
        value = 0
        for _ in range(n):
            value = (value << 8) | self.code[self.pc]
            self.pc += 1
        return value

    def instr_aconst_null(self):
        self.stack.append(None)

    def instr_iconst(self):
        opcode = self.code[self.pc - 1]
        self.stack.append(opcode - 3)

    def instr_lconst(self):
        opcode = self.code[self.pc - 1]
        self.stack.append(opcode - 9)

    def instr_fconst(self):
        opcode = self.code[self.pc - 1]
        self.stack.append(float(opcode - 11))

    def instr_dconst(self):
        opcode = self.code[self.pc - 1]
        self.stack.append(float(opcode - 14))

    def instr_bipush(self):
        value = struct.unpack('!b', bytes([self.advance()]))[0]
        self.stack.append(value)

    def instr_sipush(self):
        value = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        self.stack.append(value)

    def instr_ldc(self):
        index = self.advance()
        entry = self.constant_pool[index - 1]
        if entry.tag == 8:  # String
            string = self.constant_pool[entry.value - 1].value
            self.stack.append(string)
        elif entry.tag in (3, 4):  # Integer, Float
            self.stack.append(entry.value)
        else:
            raise ValueError(f"Unsupported ldc type: {entry.tag}")

    def instr_ldc_w(self):
        index = self.advance(2)
        entry = self.constant_pool[index - 1]
        if entry.tag == 8:  # String
            string = self.constant_pool[entry.value - 1].value
            self.stack.append(string)
        elif entry.tag in (3, 4):  # Integer, Float
            self.stack.append(entry.value)
        else:
            raise ValueError(f"Unsupported ldc_w type: {entry.tag}")

    def instr_iload(self):
        index = self.advance()
        self.stack.append(self.locals[index])

    def instr_lload(self):
        index = self.advance()
        self.stack.append(self.locals[index])

    def instr_fload(self):
        index = self.advance()
        self.stack.append(self.locals[index])

    def instr_dload(self):
        index = self.advance()
        self.stack.append(self.locals[index])

    def instr_aload(self):
        index = self.advance()
        self.stack.append(self.locals[index])

    def instr_iload_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 26
        self.stack.append(self.locals[index])

    def instr_lload_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 30
        self.stack.append(self.locals[index])

    def instr_fload_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 34
        self.stack.append(self.locals[index])

    def instr_dload_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 38
        self.stack.append(self.locals[index])

    def instr_aload_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 42
        self.stack.append(self.locals[index])

    def instr_istore(self):
        index = self.advance()
        self.locals[index] = self.stack.pop()

    def instr_lstore(self):
        index = self.advance()
        self.locals[index] = self.stack.pop()

    def instr_fstore(self):
        index = self.advance()
        self.locals[index] = self.stack.pop()

    def instr_dstore(self):
        index = self.advance()
        self.locals[index] = self.stack.pop()

    def instr_astore(self):
        index = self.advance()
        self.locals[index] = self.stack.pop()

    def instr_istore_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 59
        self.locals[index] = self.stack.pop()

    def instr_lstore_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 63
        self.locals[index] = self.stack.pop()

    def instr_fstore_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 67
        self.locals[index] = self.stack.pop()

    def instr_dstore_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 71
        self.locals[index] = self.stack.pop()

    def instr_astore_n(self):
        opcode = self.code[self.pc - 1]
        index = opcode - 75
        self.locals[index] = self.stack.pop()

    def instr_pop(self):
        self.stack.pop()

    def instr_pop2(self):
        self.stack.pop()
        self.stack.pop()

    def instr_dup(self):
        self.stack.append(self.stack[-1])

    def instr_iadd(self):
        v2, v1 = self.stack.pop(), self.stack.pop()
        self.stack.append(v1 + v2)

    def instr_isub(self):
        v2, v1 = self.stack.pop(), self.stack.pop()
        self.stack.append(v1 - v2)

    def instr_imul(self):
        v2, v1 = self.stack.pop(), self.stack.pop()
        self.stack.append(v1 * v2)

    def instr_idiv(self):
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v2 == 0:
            raise ValueError("Division by zero")
        self.stack.append(v1 // v2)

    def instr_irem(self):
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v2 == 0:
            raise ValueError("Division by zero")
        self.stack.append(v1 % v2)

    def instr_ifeq(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        if self.stack.pop() == 0:
            self.pc += offset - 3

    def instr_ifne(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        if self.stack.pop() != 0:
            self.pc += offset - 3

    def instr_iflt(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        if self.stack.pop() < 0:
            self.pc += offset - 3

    def instr_ifge(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        if self.stack.pop() >= 0:
            self.pc += offset - 3

    def instr_ifgt(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        if self.stack.pop() > 0:
            self.pc += offset - 3

    def instr_ifle(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        if self.stack.pop() <= 0:
            self.pc += offset - 3

    def instr_if_icmpeq(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v1 == v2:
            self.pc += offset - 3

    def instr_if_icmpne(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v1 != v2:
            self.pc += offset - 3

    def instr_if_icmplt(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v1 < v2:
            self.pc += offset - 3

    def instr_if_icmpge(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v1 >= v2:
            self.pc += offset - 3

    def instr_if_icmpgt(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v1 > v2:
            self.pc += offset - 3

    def instr_if_icmple(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        v2, v1 = self.stack.pop(), self.stack.pop()
        if v1 <= v2:
            self.pc += offset - 3

    def instr_goto(self):
        offset = struct.unpack('!h', bytes([self.advance(), self.advance()]))[0]
        self.pc += offset - 3

    def instr_ireturn(self):
        return self.stack.pop()

    def instr_return(self):
        return None

    def instr_getstatic(self):
        index = self.advance(2)
        field_ref = self.constant_pool[index - 1]
        class_index = field_ref.value[0]
        class_pointer = self.constant_pool[class_index - 1]
        class_name = self.constant_pool[class_pointer.value - 1].value.replace('/', '.')
        name_and_type_index = field_ref.value[1]
        name_and_type = self.constant_pool[name_and_type_index - 1].value
        name_index = name_and_type[0]
        name = self.constant_pool[name_index - 1].value
        
        # Try to resolve the static field from the class loader
        value = self.class_loader.resolve_field(class_name, name)
        if value is None:
            # Special handling for known Java system fields
            if class_name == "java.lang.System" and name == "out":
                # Return a mock PrintStream object
                class MockPrintStream:
                    def println(self, s):
                        print(s)
                value = MockPrintStream()
                self.class_loader.set_field(class_name, name, value)
            else:
                raise ValueError(f"Static field not found: {class_name}.{name}")
        self.stack.append(value)

    def instr_putstatic(self):
        index = self.advance(2)
        field_ref = self.constant_pool[index - 1]
        class_index = field_ref.value[0]
        class_pointer = self.constant_pool[class_index - 1]
        class_name = self.constant_pool[class_pointer.value - 1].value.replace('/', '.')
        name_and_type_index = field_ref.value[1]
        name_and_type = self.constant_pool[name_and_type_index - 1].value
        name_index = name_and_type[0]
        name = self.constant_pool[name_index - 1].value
        value = self.stack.pop()
        # Store the static field value in the class loader
        self.class_loader.set_field(class_name, name, value)

    def instr_getfield(self):
        index = self.advance(2)
        field_ref = self.constant_pool[index - 1]
        class_index = field_ref.value[0]
        class_pointer = self.constant_pool[class_index - 1]
        class_name = self.constant_pool[class_pointer.value - 1].value.replace('/', '.')
        name_and_type_index = field_ref.value[1]
        name_and_type = self.constant_pool[name_and_type_index - 1].value
        name_index = name_and_type[0]
        name = self.constant_pool[name_index - 1].value
        obj = self.stack.pop()
        if obj is None:
            raise ValueError("Null pointer in getfield")
        try:
            value = getattr(obj, name)
            self.stack.append(value)
        except AttributeError as e:
            key = f"{class_name}.{name}"
            if key in self.fields:
                self.stack.append(self.fields[key])
            else:
                raise ValueError(f"Failed to resolve getfield: {class_name}.{name} - {e}")

    def instr_putfield(self):
        index = self.advance(2)
        field_ref = self.constant_pool[index - 1]
        class_index = field_ref.value[0]
        class_pointer = self.constant_pool[class_index - 1]
        class_name = self.constant_pool[class_pointer.value - 1].value.replace('/', '.')
        name_and_type_index = field_ref.value[1]
        name_and_type = self.constant_pool[name_and_type_index - 1].value
        name_index = name_and_type[0]
        name = self.constant_pool[name_index - 1].value
        value = self.stack.pop()
        obj = self.stack.pop()
        if obj is None:
            raise ValueError("Null pointer in putfield")
        try:
            setattr(obj, name, value)
            self.fields[f"{class_name}.{name}"] = value
        except AttributeError as e:
            self.fields[f"{class_name}.{name}"] = value

    def instr_invokevirtual(self):
        index = self.advance(2)
        method_ref = self.constant_pool[index - 1]
        name_and_type = self.constant_pool[method_ref.value[1] - 1].value
        name = self.constant_pool[name_and_type[0] - 1].value
        typee = self.constant_pool[name_and_type[1] - 1].value
        arg_num = len(typee.split(';')) - 1
        args = [self.stack.pop() for _ in range(arg_num)]
        args.reverse()
        obj = self.stack.pop()
        if obj is None:
            raise ValueError("Null pointer in invokevirtual")
        try:
            target_method = getattr(obj, name)
            result = target_method(*args)
            if typee.startswith('()') and typee != '()V':
                self.stack.append(result)
        except AttributeError as e:
            raise ValueError(f"Failed to invoke virtual method: {name}{typee} - {e}")

    def instr_invokespecial(self):
        index = self.advance(2)
        method_ref = self.constant_pool[index - 1]
        class_index = method_ref.value[0]
        class_pointer = self.constant_pool[class_index - 1]
        class_name = self.constant_pool[class_pointer.value - 1].value.replace('/', '.')
        name_and_type = self.constant_pool[method_ref.value[1] - 1].value
        name = self.constant_pool[name_and_type[0] - 1].value
        typee = self.constant_pool[name_and_type[1] - 1].value
        arg_num = len(typee.split(';')) - 1
        args = [self.stack.pop() for _ in range(arg_num)]
        args.reverse()
        obj = self.stack.pop()
        if obj is None:
            raise ValueError("Null pointer in invokespecial")
        
        # Try to get method from the loaded class
        code = self.class_loader.get_method_code(class_name, name)
        if code:
            sub_interpreter = Interpreter(code[2], code[0], code[1], 
                                        self.class_loader.load_class(class_name).constant_pool, 
                                        self.class_loader)
            # Set up locals: 'this' reference plus arguments
            sub_interpreter.locals[0] = obj
            sub_interpreter.locals[1:len(args)+1] = args
            result = sub_interpreter.run()
            if typee.startswith('()') and typee != '()V':
                self.stack.append(result)
        else:
            # For system methods like Object.<init>, just ignore
            if class_name.startswith("java."):
                pass  # Ignore Java standard library method calls
            else:
                raise ValueError(f"Failed to invoke special method: {class_name}.{name}{typee}")

    def instr_invokestatic(self):
        index = self.advance(2)
        method_ref = self.constant_pool[index - 1]
        class_index = method_ref.value[0]
        class_pointer = self.constant_pool[class_index - 1]
        class_name = self.constant_pool[class_pointer.value - 1].value.replace('/', '.')
        name_and_type = self.constant_pool[method_ref.value[1] - 1].value
        name = self.constant_pool[name_and_type[0] - 1].value
        typee = self.constant_pool[name_and_type[1] - 1].value
        arg_num = len(typee.split(';')) - 1
        args = [self.stack.pop() for _ in range(arg_num)]
        args.reverse()
        
        # Try to load and execute method from class loader
        code = self.class_loader.get_method_code(class_name, name)
        if code:
            sub_interpreter = Interpreter(code[2], code[0], code[1], 
                                        self.class_loader.load_class(class_name).constant_pool, 
                                        self.class_loader)
            sub_interpreter.locals[:len(args)] = args
            result = sub_interpreter.run()
            if typee.startswith('()') and typee != '()V':
                self.stack.append(result)
        else:
            raise ValueError(f"Failed to invoke static method: {class_name}.{name}{typee}")

    def instr_invokeinterface(self):
        index = self.advance(2)
        count = self.advance()
        zero = self.advance()
        if zero != 0:
            raise ValueError("Invalid invokeinterface format: fourth byte must be zero")
        method_ref = self.constant_pool[index - 1]
        name_and_type = self.constant_pool[method_ref.value[1] - 1].value
        name = self.constant_pool[name_and_type[0] - 1].value
        typee = self.constant_pool[name_and_type[1] - 1].value
        arg_num = len(typee.split(';')) - 1
        args = [self.stack.pop() for _ in range(arg_num)]
        args.reverse()
        obj = self.stack.pop()
        if obj is None:
            raise ValueError("Null pointer in invokeinterface")
        try:
            target_method = getattr(obj, name)
            result = target_method(*args)
            if typee.startswith('()') and typee != '()V':
                self.stack.append(result)
        except AttributeError as e:
            raise ValueError(f"Failed to invoke interface method: {name}{typee} - {e}")

    def run(self) -> Optional[Any]:
        while self.pc < len(self.code):
            opcode = self.advance()
            if opcode not in self.instructions:
                raise ValueError(f"Unsupported opcode: {opcode} at pc={self.pc-1}")
            result = self.instructions[opcode]()
            if opcode in (172, 177):
                return result
            if opcode in (170, 171, 196):
                raise ValueError(f"Unsupported complex opcode: {opcode} at pc={self.pc-1}")
