import unittest
from tac_to_llvm import TACToLLVMConverter

class TestTACToLLVMConverter(unittest.TestCase):
    def setUp(self):
        self.converter = TACToLLVMConverter()

    def test_basic_operations(self):
        tac_code = [
            "t0 = LOAD 4",
            "t1 = LOAD 2",
            "t2 = + t0 t1",
            "sum.g = t2"
        ]
        
        llvm_ir = self.converter.convert(tac_code)
        
        # Verify key components in generated IR
        self.assertIn("define i32 @main()", llvm_ir)
        self.assertIn("alloca i32", llvm_ir)
        self.assertIn("store i32 4", llvm_ir)
        self.assertIn("store i32 2", llvm_ir)
        self.assertIn("add i32", llvm_ir)

    def test_undefined_variable(self):
        tac_code = [
            "t0 = LOAD 4",
            "t1 = LOAD 2",
            "t2 = + t0 t1",
            "t3 = LOAD z",  # Should raise error
            "t4 = + t2 t3",
            "sum.g = t4"
        ]
        
        with self.assertRaises(ValueError) as context:
            self.converter.convert(tac_code)
        
        self.assertIn("Undefined variable: z", str(context.exception))

if __name__ == '__main__':
    unittest.main()