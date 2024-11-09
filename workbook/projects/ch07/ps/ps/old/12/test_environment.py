import unittest
from environment import Environment

class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = Environment()

    def test_variable_definition_and_lookup(self):
        self.env.define('x', 10)
        result = self.env.lookup('x')
        self.assertEqual(result, 10)

    def test_procedure_definition_and_invocation(self):
        def add(a, b):
            return a + b
        self.env.define('add', add)
        result = self.env.invoke('add', 2, 3)
        self.assertEqual(result, 5)

    def test_scoping(self):
        self.env.define('x', 10)
        self.env.enter_scope()
        self.env.define('x', 20)
        result = self.env.lookup('x')
        self.assertEqual(result, 20)
        self.env.exit_scope()
        result = self.env.lookup('x')
        self.assertEqual(result, 10)

    def test_define_and_lookup_dict(self):
        self.env.define('my_dict', {'a': 1, 'b': 2})
        result = self.env.lookup('my_dict')
        self.assertEqual(result, {'a': 1, 'b': 2})

    def test_add_to_dict(self):
        self.env.define('my_dict', {'a': 1, 'b': 2})
        self.env.add_to_dict('my_dict', 'c', 3)
        result = self.env.lookup('my_dict')
        self.assertEqual(result, {'a': 1, 'b': 2, 'c': 3})

    def test_lookup_in_dict(self):
        self.env.define('my_dict', {'a': 1, 'b': 2})
        result = self.env.lookup_in_dict('my_dict', 'b')
        self.assertEqual(result, 2)

    def test_dict_key_not_found(self):
        self.env.define('my_dict', {'a': 1, 'b': 2})
        with self.assertRaises(KeyError):
            self.env.lookup_in_dict('my_dict', 'c')

    def test_add_to_non_dict(self):
        self.env.define('x', 10)
        with self.assertRaises(TypeError):
            self.env.add_to_dict('x', 'a', 5)

if __name__ == '__main__':
    unittest.main()