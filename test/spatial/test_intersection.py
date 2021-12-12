import unittest

from robot.spatial import Intersection

class TestIntersection(unittest.TestCase):
  def setUp(self):
    self.miss = Intersection.Miss()
    self.near = Intersection(0.5, 'a')
    self.far  = Intersection(1.0, 'b')

  def test_negative_t_throws(self):
    with self.assertRaises(AssertionError):
      Intersection(-1.0, None)

  def test_t_and_obj_are_optional(self):
    x = Intersection(None, None)

    self.assertIsNone(x.t)
    self.assertIsNone(x.obj)

  def test_t_and_obj_are_immutable(self):
    t = 1.0
    obj = 'Something'
    x = Intersection(t, obj)

    with self.assertRaises(AttributeError):
      x.t = None

    with self.assertRaises(AttributeError):
      x.obj = None

    self.assertAlmostEqual(x.t, t)
    self.assertEqual(x.obj, obj)

  def test_intersection_miss_factory_is_not_hit(self):
    self.assertFalse(self.miss.hit)

  def test_positive_t_is_hit_regardless_of_obj(self):
    xs = [
      Intersection(0, None),
      Intersection(1.0, None),
      Intersection(1.0, 'Something')
    ]

    for x in xs:
      with self.subTest(f'With object: {x.obj}'):
        self.assertTrue(x.hit)

  def test_closer_than_for_found_intersections(self):
    self.assertTrue(self.near.closer_than(self.far))
    self.assertFalse(self.far.closer_than(self.near))

  def test_closer_than_always_returns_true_valid_against_miss(self):
    self.assertTrue(self.near.closer_than(self.miss))

  def test_closer_than_always_returns_false_for_a_miss(self):
    for x in [self.miss, self.near, self.far]:
      with self.subTest(f'Against intersection t: {x.t}'):
        self.assertFalse(self.miss.closer_than(x))

  def test_closer_than_always_returns_false_for_identical_intersections(self):
    for x in [self.miss, self.near, self.far]:
      with self.subTest(f'Against intersection t: {x.t}'):
        self.assertFalse(x.closer_than(x))