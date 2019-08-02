import math, unittest

from robot.mech.joint        import DenavitHartenberg, JointLimits, Joint
from robot.spatial.vector3   import Vector3
from robot.spatial.transform import Transform

class TestJoint(unittest.TestCase):
  def setUp(self):
    self.dh = DenavitHartenberg(math.radians(45), 50, math.radians( 180), 72)
    self.limits = JointLimits(math.radians(400), math.radians(-400))
    self.joint = Joint(self.dh, self.limits)

  def test_init(self):
    # Check that limits are swapped
    expected = JointLimits(math.radians(-400), math.radians(400))

    result = self.joint.limits

    self.assertEqual(result.low, expected.low)
    self.assertEqual(result.high, expected.high)

  def test_transform(self):
    q = math.radians(30)

    d = Transform.from_axis_angle_translation(translation = Vector3(0, 0, self.joint.dh.d))
    theta = Transform.from_axis_angle_translation(axis = Vector3(0, 0, 1), angle = self.joint.dh.theta + q)
    a = Transform.from_axis_angle_translation(translation = Vector3(self.joint.dh.a, 0, 0))
    alpha = Transform.from_axis_angle_translation(axis = Vector3(1, 0, 0), angle = self.joint.dh.alpha)

    expected = d * theta * a * alpha
    self.joint.angle = q
    result = self.joint.transform

    self.assertAlmostEqual(result.dual, expected.dual)

  def test_num_revolutions(self):
    low = self.joint.limits.low
    high = self.joint.limits.high

    expected = math.floor((high - low) / (2 * math.pi))
    result = self.joint.num_revolutions()

    self.assertEqual(result, expected)
