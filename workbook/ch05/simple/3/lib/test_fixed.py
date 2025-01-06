import unittest
from fixed import FixedPoint, sqrt_fixed  # Replace with the actual filename/module name

class TestFixedPoint(unittest.TestCase):
    def setUp(self):
        """Set up fixed-point numbers for testing."""
        self.fp1 = FixedPoint(2.3)  # FixedPoint(value=150732, float_equiv=2.299988)
        self.fp2 = FixedPoint(1.5)  # FixedPoint(value=98304, float_equiv=1.500000)

    def test_representation(self):
        """Test the fixed-point representation."""
        self.assertEqual(self.fp1.value, 150732)
        self.assertAlmostEqual(self.fp1.to_float(), 2.299988, places=5)
        self.assertEqual(self.fp2.value, 98304)
        self.assertAlmostEqual(self.fp2.to_float(), 1.500000, places=5)

    def test_addition(self):
        """Test addition of fixed-point numbers."""
        result = self.fp1 + self.fp2
        self.assertEqual(result.value, 249036)
        self.assertAlmostEqual(result.to_float(), 3.799988, places=5)

    def test_subtraction(self):
        """Test subtraction of fixed-point numbers."""
        result = self.fp1 - self.fp2
        self.assertEqual(result.value, 52428)
        self.assertAlmostEqual(result.to_float(), 0.799988, places=5)

    def test_multiplication(self):
        """Test multiplication of fixed-point numbers."""
        result = self.fp1 * self.fp2
        self.assertEqual(result.value, 226098)
        self.assertAlmostEqual(result.to_float(), 3.449982, places=5)

    def test_division(self):
        """Test division of fixed-point numbers."""
        result = self.fp1 / self.fp2
        self.assertEqual(result.value, 100488)
        self.assertAlmostEqual(result.to_float(), 1.533325, places=5)

    def test_sqrt(self):
        """Test square root of a fixed-point number."""
        result = sqrt_fixed(self.fp1)
        self.assertEqual(result.value, 99390)
        self.assertAlmostEqual(result.to_float(), 1.516571, places=5)

    def test_invalid_operations(self):
        """Test operations with unsupported types."""
        with self.assertRaises(ValueError):
            self.fp1 + "invalid"

        with self.assertRaises(ValueError):
            sqrt_fixed(FixedPoint(-1))

if __name__ == "__main__":
    unittest.main()
