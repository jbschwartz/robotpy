import math, unittest

from robot.spatial.vector3 import angle_between, normalize, Vector3

class TestVector3(unittest.TestCase):
  def setUp(self):
    self.v1 = Vector3(-1, 2, -3)
    self.v2 = Vector3(2, -5, 3)
    self.s = 2.5

  def test_init(self):
    '''
    Vector instances default to zero vector
    '''
    v = Vector3()
    self.assertEqual(v, Vector3(0, 0, 0))

  def test_add(self):
    expected = Vector3(1, -3, 0)
    self.assertEqual(self.v1 + self.v2, expected)
    self.assertEqual(self.v2 + self.v1, expected)

  def test_sub(self):
    expected = Vector3(-3, 7, -6)
    self.assertEqual(self.v1 - self.v2, expected)

  def test_neg(self):
    expected = Vector3(1, -2, 3)
    self.assertEqual(-self.v1, expected)

  def test_mul(self):
    '''
    Vector left and right scalar and dot product
    '''

    # Dot product
    expected = -21
    self.assertEqual(self.v1 * self.v2, expected)
    self.assertEqual(self.v2 * self.v1, expected)

    # Scalar multiplication
    expected = Vector3(self.s * self.v1.x, self.s * self.v1.y, self.s * self.v1.z)
    self.assertAlmostEqual(self.v1 * self.s, expected)
    self.assertAlmostEqual(self.s * self.v1, expected)

  def test_truediv(self):
    '''
    Vector scalar division
    '''

    expected = Vector3(self.v1.x / self.s, self.v1.y / self.s, self.v1.z / self.s)
    self.assertAlmostEqual(self.v1 / self.s, expected)

  def test_getitem(self):
    # Test to ensure vector is iterated in xyz order
    expecteds = [ self.v1.x, self.v1.y, self.v1.z ]
    for index, component in enumerate(self.v1):
      self.assertEqual(component, expecteds[index])

  def test_length(self):
    expected = math.sqrt(14)
    self.assertAlmostEqual(self.v1.length(), expected)

  def test_length_sq(self):
    expected = 14
    self.assertAlmostEqual(self.v1.length_sq(), expected)

  def test_is_unit(self):
    unit_vector = normalize(self.v1)
    self.assertFalse(self.v1.is_unit())
    self.assertTrue(unit_vector.is_unit())

  def test_normalize(self):
    length = self.v1.length()
    expected = self.v1 / length
    self.v1.normalize()

    self.assertAlmostEqual(self.v1, expected)
    self.assertAlmostEqual(self.v1.length(), 1)

  def test_vector3_normalize(self):
    result = normalize(self.v1)

    self.v1.normalize()
    expected = self.v1

    self.assertEqual(result, expected)

  def test_vector3_angle_between(self):
    expected = 0
    self.assertAlmostEqual(angle_between(self.v1, 5 * self.v1), expected)

    x = Vector3.X()
    y = Vector3.Y()

    expected = math.radians(90)
    self.assertAlmostEqual(angle_between(x, y), expected)
    self.assertAlmostEqual(angle_between(y, x), expected)

    p = Vector3(45, 45, 0)

    expected = math.radians(45)
    self.assertAlmostEqual(angle_between(x, p), expected)
    self.assertAlmostEqual(angle_between(p, x), expected)

  def test_vector3_cross(self):
    expected = Vector3(-9, -3, 1)
    self.assertAlmostEqual(self.v1 % self.v2, expected)

    expected = Vector3(9, 3, -1)
    self.assertAlmostEqual(self.v2 % self.v1, expected)

  @unittest.skip("Need to write test")
  def test_almost_equal(self):
    self.assertTrue(False)
