import unittest

from robot.spatial.aabb    import AABB
from robot.spatial.vector3 import Vector3

class TestAABB(unittest.TestCase):
  def setUp(self):
    self.aabb = AABB()
    self.v1 = Vector3(1, 2, 3)
    self.v2 = Vector3(-1, -2, -3)
    self.v3 = Vector3(0, 1, 2)
    self.v4 = Vector3(4, 4, 4)

    self.aabb.extend(self.v1, self.v2, self.v3)

  def test_extend(self):
    self.assertAlmostEqual(self.v2, self.aabb.min)
    self.assertAlmostEqual(self.v1, self.aabb.max)

  def test_extend_aabb(self):
    other_aabb = AABB()
    other_aabb.extend(self.v3, self.v4)

    self.aabb.extend(other_aabb)
    
    self.assertAlmostEqual(self.v2, self.aabb.min)
    self.assertAlmostEqual(self.v4, self.aabb.max)

  def test_size(self):
    expected = self.v1 - self.v2

    self.assertAlmostEqual(self.aabb.size, expected)

  def test_center(self):
    expected = (self.v1 - self.v2) / 2 + self.v2

    self.assertAlmostEqual(self.aabb.center, expected)