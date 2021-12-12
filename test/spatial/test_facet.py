import unittest

from robot.spatial import Facet, Intersection, Ray, Vector3

class TestFacet(unittest.TestCase):
  def setUp(self):
    self.vertices = [
       Vector3.X(),
       Vector3.Y(),
      -Vector3.X()
    ]
    self.facet = Facet(self.vertices)

    self.origins = [
      Vector3(0, 0, 0),
      Vector3(0, 0, 1),
      Vector3(5, 5, 5)
    ]

  def test_intersect(self):
    def compute_t(ray, intersection):
      '''Backwards compute parameter t given a ray and intersection'''
      if intersection is not None:
        return (ray.origin - intersection).length()
      else:
        return None

    rays = [
      Ray(self.origins[0],  Vector3.Z()),
      Ray(self.origins[0], -Vector3.Z()),
      Ray(self.origins[1], -Vector3.Z()),
      Ray(self.origins[1],  Vector3.Z()),
      Ray(self.origins[1],  Vector3(0.5, 0.25, -1)),
      Ray(self.origins[2], -Vector3.Z()),
      Ray(self.origins[2],  Vector3(-1, -1, -1))
    ]

    intersections = [
      None,
      self.origins[0],
      self.origins[0],
      None,
      Vector3(0.5, 0.25, 0),
      None,
      Vector3(),
    ]

    expecteds = [
      Intersection(compute_t(ray, intersection), None)
      for ray, intersection in zip(rays, intersections)
    ]

    for (ray, expected) in zip(rays, expecteds):
      with self.subTest(f"Check {ray}"):
        result = self.facet.intersect(ray)

        if expected.hit:
          self.assertAlmostEqual(result.t, expected.t)
