import unittest
from environment import Environment

class TestEnvironment(unittest.TestCase):
    def setUp(self):
        """Set up a fresh Environment instance for each test."""
        self.env = Environment()

    def test_define_and_lookup(self):
        """Test defining and looking up variables in the environment."""
        self.env.define("x", 10)
        self.env.define("y", 20)

        # Test if the values are correctly stored
        self.assertEqual(self.env.lookup("x"), 10)
        self.assertEqual(self.env.lookup("y"), 20)

    def test_lookup_non_existent_variable(self):
        """Test lookup for a non-existent variable raises an error."""
        with self.assertRaises(KeyError):
            self.env.lookup("z")

    def test_scope_management(self):
        """Test entering and exiting scopes."""
        self.env.define("a", 5)
        self.assertEqual(self.env.lookup("a"), 5)

        # a new scope and define new variable
        self.env.enter_scope()
        self.env.define("b", 10)
        self.assertEqual(self.env.lookup("b"), 10)

        # ensure that variable in inner scope does not leak to outer scope
        self.env.exit_scope()
        with self.assertRaises(KeyError):
            self.env.lookup("b")

        # outer scope variable should still be accessible
        self.assertEqual(self.env.lookup("a"), 5)

    def test_redefine_variable(self):
        """Test redefining a variable in the current scope."""
        self.env.define("x", 10)
        self.assertEqual(self.env.lookup("x"), 10)

        # Redefine 'x' with a new value
        self.env.define("x", 100)
        self.assertEqual(self.env.lookup("x"), 100)

    def test_lookup_after_exit_scope(self):
        """Ensure variables are properly scoped when exiting."""
        self.env.enter_scope()
        self.env.define("x", 10)
        self.assertEqual(self.env.lookup("x"), 10)

        self.env.exit_scope()
        with self.assertRaises(KeyError):
            self.env.lookup("x")

    def test_error_handling_define_invalid(self):
        """Test error handling when defining invalid values."""
        with self.assertRaises(TypeError):
            self.env.define("invalid_name", None)  # cannot define None value

if __name__ == "__main__":
    unittest.main()
