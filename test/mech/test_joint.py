import unittest
import math

from robot.spatial import Vector3, Transform
from robot.mech import Joint

class TestJoint(unittest.TestCase):
  def setUp(self):
    self.joint = Joint(math.radians(45), 50, math.radians( 180), 72, { 'low': math.radians(400), 'high': math.radians(-400) })

  def test_init(self):
    # Check that limits are swapped
    expected = {
      'low': math.radians(-400),
      'high': math.radians(400)
    }
    result = self.joint.limits

    self.assertEqual(result['low'], expected['low'])
    self.assertEqual(result['high'], expected['high'])

  def test_transform(self):
    q = math.radians(30)

    d = Transform(translation = Vector3(0, 0, self.joint.dh['d']))
    theta = Transform(axis = Vector3(0, 0, 1), angle = self.joint.dh['theta'] + q)
    a = Transform(translation = Vector3(self.joint.dh['a'], 0, 0))
    alpha = Transform(axis = Vector3(1, 0, 0), angle = self.joint.dh['alpha'])

    expected = d * theta * a * alpha
    result = self.joint.transform(q)

    self.assertAlmostEqual(result.dual, expected.dual)

  def test_num_revolutions(self):
    low = self.joint.limits['low']
    high = self.joint.limits['high']

    expected = math.floor((high - low) / (2 * math.pi))
    result = self.joint.num_revolutions()

    self.assertEqual(result, expected)
