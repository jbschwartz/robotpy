import math, unittest

from robot.spatial.ray     import Ray
from robot.spatial.vector3 import Vector3
from robot.visual.facet    import Facet

class TestFacet(unittest.TestCase):
  def setUp(self):
    self.vertices = [
      Vector3(1, 0, 0),
      Vector3(0, 1, 0),
      Vector3(-1, 0, 0)
    ]
    self.facet = Facet(self.vertices)

    self.origins = [
      Vector3(0, 0, 0),
      Vector3(0, 0, 1),
      Vector3(5, 5, 5)
    ]

  def test_intersect(self):
    rays = [
      (Ray(self.origins[0], Vector3(0, 0,  1)), None),
      (Ray(self.origins[0], Vector3(0, 0, -1)), self.origins[0] ),
      (Ray(self.origins[1], Vector3(0, 0, -1)), self.origins[0] ),
      (Ray(self.origins[1], Vector3(0, 0,  1)), None),
      (Ray(self.origins[1], Vector3(0.5, 0.25, -1)), Vector3(0.5, 0.25, 0)),
      (Ray(self.origins[2], Vector3(0, 0, -1)), None),
      (Ray(self.origins[2], Vector3(-1, -1, -1)), Vector3()),
    ]
    
    for (ray, expected) in rays:
      with self.subTest(f"Check {ray}"):
        result = self.facet.intersect(ray)

        if expected is None:
          self.assertIsNone(result)
        else:
          self.assertAlmostEqual(result, expected)
