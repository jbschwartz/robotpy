import math, unittest

from robot.spatial import Ray, vector3

Vector3 = vector3.Vector3

class TestRay(unittest.TestCase):
  def setUp(self):
    self.direction = Vector3(-1, 4, 5)
    self.ray = Ray(Vector3(1, 2, 3), self.direction)

  def test_init(self):
    result = self.ray.direction
    expected = vector3.normalize(self.direction)

    self.assertAlmostEqual(result, expected)

  def test_evaluate(self):
    # TODO: Needs more testing
    result = self.ray.evaluate(0)
    expected = self.ray.origin

    self.assertAlmostEqual(result, expected)