import math, unittest

from robot.mech.joint        import DenavitHartenberg, JointLimits, Joint
from robot.spatial.vector3   import Vector3
from robot.spatial.transform import Transform

class TestJoint(unittest.TestCase):
  def setUp(self):
    dh     = DenavitHartenberg(math.radians(45), 50, math.radians( 180), 72)
    limits = JointLimits(math.radians(400), math.radians(-400))
    self.joint = Joint(dh, limits)

  def test_init(self):
    # Check that limits are swapped
    expected = JointLimits(math.radians(-400), math.radians(400))

    for component in self.joint.limits._fields:
      self.assertEqual(getattr(self.joint.limits, component), getattr(expected, component))

  def test_transform(self):
    self.joint.angle = math.radians(30)

    theta = Transform.from_axis_angle_translation(axis = Vector3(0, 0, 1), angle = self.joint.dh.theta + self.joint.angle)
    alpha = Transform.from_axis_angle_translation(axis = Vector3(1, 0, 0), angle = self.joint.dh.alpha)
    d     = Transform.from_axis_angle_translation(translation = Vector3(0, 0, self.joint.dh.d))
    a     = Transform.from_axis_angle_translation(translation = Vector3(self.joint.dh.a, 0, 0))

    expected = d * theta * a * alpha

    self.assertAlmostEqual(self.joint.transform.dual, expected.dual)

  def test_travel_in_revs(self):
    expected = math.floor((self.joint.limits.high - self.joint.limits.low) / (2 * math.pi))

    self.assertEqual(self.joint.travel_in_revs(), expected)
