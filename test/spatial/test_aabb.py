import unittest

from robot.spatial import AABB
from robot.spatial import Vector3

class TestAABB(unittest.TestCase):
  def setUp(self):
    self.aabb = AABB()

  def test_extend(self):
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(-1, -2, -3)
    v3 = Vector3(0, 1, 2)
    
    self.aabb.extend(v1)

    print(self.aabb.min, self.aabb.max)

    self.assertAlmostEqual(v1, self.aabb.min)
    self.assertAlmostEqual(v1, self.aabb.max)

    self.aabb.extend(v2)

    self.assertAlmostEqual(v2, self.aabb.min)
    self.assertAlmostEqual(v1, self.aabb.max)

    self.aabb.extend(v3)

    self.assertAlmostEqual(v2, self.aabb.min)
    self.assertAlmostEqual(v1, self.aabb.max)