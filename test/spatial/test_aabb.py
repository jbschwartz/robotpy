import unittest

from robot.spatial import AABB, Ray, Vector3

class TestAABB(unittest.TestCase):
  def setUp(self):
    self.v1 = Vector3(1, 2, 3)
    self.v2 = Vector3(-1, -2, -3)
    self.v3 = Vector3(0, 1, 2)
    self.v4 = Vector3(4, 4, 4)

    self.aabb = AABB.from_points([self.v1, self.v2, self.v3])

  def test_expand(self):
    self.assertAlmostEqual(self.v2, self.aabb.min)
    self.assertAlmostEqual(self.v1, self.aabb.max)

  def test_expand_aabb(self):
    other_aabb = AABB(self.v3, self.v4)

    self.aabb.expand(other_aabb)

    self.assertAlmostEqual(self.v2, self.aabb.min)
    self.assertAlmostEqual(self.v4, self.aabb.max)

  def test_split(self):
    # TODO: Make this into a nice decorator to sprinkle throughout test cases
    self.longMessage = False

    value = -0.5

    for index in range(0, 3):
    # for axis in [AXIS.X, AXIS.Y, AXIS.Z]:
      with self.subTest(f'Split on axis {index}'):
        left, right = self.aabb.split(index, value)

        left_max  = Vector3(*self.v1)
        left_max[index] = value

        right_min = Vector3(*self.v2)
        right_min[index] = value

        self.assertAlmostEqual(left.min, self.aabb.min, msg='Left split incorrect minimum')
        self.assertAlmostEqual(left.max, left_max, msg='Left split incorrect maximum')

        self.assertAlmostEqual(right.min, right_min, msg='Right split incorrect minimum')
        self.assertAlmostEqual(right.max, self.aabb.max, msg='Right split incorrect maximum')

  def test_size(self):
    expected = self.v1 - self.v2

    self.assertAlmostEqual(self.aabb.size, expected)

  def test_center(self):
    expected = (self.v1 - self.v2) / 2 + self.v2

    self.assertAlmostEqual(self.aabb.center, expected)

  def test_center_on_empty_aabb_is_origin(self):
    empty = AABB()

    self.assertAlmostEquals(empty.center, Vector3(0, 0, 0))

  def test_is_empty_is_true_for_default_constructed_aabb(self):
    empty = AABB()

    self.assertTrue(empty.is_empty)

  def test_is_empty_is_false_for_expanded_aabb(self):
    self.assertFalse(self.aabb.is_empty)

  def test_contains(self):
    # Test contains with points
    self.assertTrue(self.aabb.contains(self.v3))
    self.assertFalse(self.aabb.contains(self.v4))

  def test_intersect(self):
    origin = Vector3(2, 3, 1)

    pairs = [
      (Ray(origin, Vector3( 1,  0,  0)), False),
      (Ray(origin, Vector3(-1,  0,  0)), False),
      (Ray(origin, Vector3( 0,  1,  0)), False),
      (Ray(origin, Vector3( 0, -1,  0)), False),
      (Ray(origin, Vector3( 0,  0,  1)), False),
      (Ray(origin, Vector3( 0,  0, -1)), False),
      (Ray(origin, Vector3(-2,  1,  1)), False),
      (Ray(origin, Vector3(-1,  0,  1)), False),
      (Ray(origin, Vector3(-1, -1,  1)), True),
      (Ray(origin, Vector3(-1, -1,  0)), True),
      (Ray(origin, Vector3(-2, -1,  0)), True)
    ]

    for index, (ray, expected) in enumerate(pairs):
      with self.subTest(msg=f"Test #{index}, Ray {ray}"):
        self.assertEqual(self.aabb.intersect(ray), expected)