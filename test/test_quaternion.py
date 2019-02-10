import unittest
import math

from robot.spatial import Quaternion 
class TestQuaternion(unittest.TestCase):
  def setUp(self):
    self.I = Quaternion()
    self.q = Quaternion(1, 2, 3, 4)
    self.r = Quaternion(4, -3, 2, -1)
  def test_init(self):
    '''
    Quaternion instances default to multiplicative identity quaternion
    '''
    self.assertEqual(self.I, Quaternion(1, 0, 0, 0))
  def test_add(self):
    expected = Quaternion(5, -1, 5, 3)
    self.assertEqual(self.q + self.r, expected)
    self.assertEqual(self.r + self.q, expected)
  def test_sub(self):
    expected = Quaternion(-3, 5, 1, 5)
    self.assertEqual(self.q - self.r, expected)
  def test_neg(self):
    expected = Quaternion(-4, 3, -2, 1)
    self.assertEqual(-self.r, expected)
  def test_mul(self):
    '''
    Quaternion left and right scalar and quaternion multiplication
    '''

    # Quaternion multiplication
    self.assertEqual(self.I * self.q, self.q)
    self.assertEqual(self.q * self.I, self.q)

    expected = Quaternion(8, -6, 4, 28)
    self.assertEqual(self.q * self.r, expected)

    expected = Quaternion(8, 16, 24, 2)
    self.assertEqual(self.r * self.q, expected)

    # Scalar multiplication
    s = 2.5
    expected = Quaternion(s * self.q.r, s * self.q.x, s * self.q.y, s * self.q.z)
    self.assertAlmostEqual(self.q * s, expected)
    self.assertAlmostEqual(s * self.q, expected)
  def test_truediv(self):
    '''
    Quaternion scalar division
    '''
    s = 2
    expected = Quaternion(self.q.r / s, self.q.x / s, self.q.y / s, self.q.z / s)
    self.assertAlmostEqual(self.q / s, expected)
  def test_conjugate(self):
    expected = Quaternion(self.q.r, -self.q.x, -self.q.y, -self.q.z) 
    self.q.conjugate()
    self.assertEqual(self.q, expected)
  def test_norm(self):
    expected = math.sqrt(30)
    self.assertAlmostEqual(self.q.norm(), expected)
  def test_normalize(self):
    norm = self.q.norm()
    expected = self.q / norm
    self.q.normalize()

    self.assertAlmostEqual(self.q.r, expected.r)
    self.assertAlmostEqual(self.q.x, expected.x)
    self.assertAlmostEqual(self.q.y, expected.y)
    self.assertAlmostEqual(self.q.z, expected.z)
    self.assertAlmostEqual(self.q.norm(), 1)