import unittest
import math

from robot.spatial import Vector3
import robot.spatial.vector3 as vector3

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

  def test_lengthSq(self):
    expected = 14
    self.assertAlmostEqual(self.v1.lengthSq(), expected)

  def test_normalize(self):
    length = self.v1.length()
    expected = self.v1 / length
    self.v1.normalize()

    self.assertAlmostEqual(self.v1, expected)
    self.assertAlmostEqual(self.v1.length(), 1)

  def test_vector3_normalize(self):
    result = vector3.normalize(self.v1)

    self.v1.normalize()
    expected = self.v1

    self.assertEqual(result, expected)

  def test_vector3_angleBetween(self):
    expected = 0
    self.assertAlmostEqual(vector3.angleBetween(self.v1, 5 * self.v1), expected)

    x = Vector3(1, 0, 0)
    y = Vector3(0, 1, 0)

    expected = math.radians(90)
    self.assertAlmostEqual(vector3.angleBetween(x, y), expected)
    self.assertAlmostEqual(vector3.angleBetween(y, x), expected)

    p = Vector3(45, 45, 0)

    expected = math.radians(45)
    self.assertAlmostEqual(vector3.angleBetween(x, p), expected)
    self.assertAlmostEqual(vector3.angleBetween(p, x), expected)

  def test_vector3_cross(self):
    expected = Vector3(-9, -3, 1)
    self.assertAlmostEqual(vector3.cross(self.v1, self.v2), expected)

    expected = Vector3(9, 3, -1)
    self.assertAlmostEqual(vector3.cross(self.v2, self.v1), expected)
