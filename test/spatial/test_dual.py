import unittest

from robot.spatial import Dual, Quaternion

class TestDual(unittest.TestCase):
  def setUp(self):
    self.r1 = Quaternion(1, 2, 3, 4)
    self.d1 = Quaternion(0, 1, 2, 3)
    self.r2 = Quaternion(0, -1, 0, 0)
    self.d2 = Quaternion(1, 3, -4, 5)

    self.dq1 = Dual(self.r1, self.d1)
    self.dq2 = Dual(self.r2, self.d2)

    self.s = 2.5

  def test_add(self):
    expected = Dual(self.r1 + self.r2, self.d1 + self.d2)
    self.assertEqual(self.dq1 + self.dq2, expected)

  def test_sub(self):
    expected = Dual(self.r1 - self.r2, self.d1 - self.d2)
    self.assertEqual(self.dq1 - self.dq2, expected)

  def test_mul(self):
    '''
    Dual quaternion left and right scalar and dual multiplication
    '''

    expected = Dual(self.r1 * self.r2, self.r1 * self.d2 + self.d1 * self.r2)
    self.assertEqual(self.dq1 * self.dq2, expected)

    expected = Dual(self.r2 * self.r1, self.r2 * self.d1 + self.d2 * self.r1)
    self.assertEqual(self.dq2 * self.dq1, expected)

    expected = Dual(self.s * self.r1, self.s * self.d1)
    self.assertEqual(self.s * self.dq1, expected)
    self.assertEqual(self.dq1 * self.s, expected)

  def test_truediv(self):
    expected = Dual(self.r1 / self.s, self.d1 / self.s)
    self.assertEqual(self.dq1 / self.s, expected)

  def test_conjugate(self):
    d = Dual(1, 2)
    d.conjugate()
    expected = Dual(1, -2)
    self.assertEqual(d, expected)