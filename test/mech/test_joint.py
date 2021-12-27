import math, unittest

from collections import namedtuple

from robot                   import constant
from robot.mech.exceptions   import InvalidJointAngleError, InvalidJointDictError
from robot.mech.joint        import DenavitHartenberg, JointLimits, Joint
from spatial                 import Transform, Vector3

def create_dummy_dict(dh: dict = None, limits: dict = None, home: int = None):
  """Create a sample dictionary with all of the DH fields present."""
  defaults = {
    tup: {k: v for k, v in zip(tup._fields, range(0, len(tup._fields)))}
    for tup in (DenavitHartenberg, JointLimits)
  }

  defaults['home'] = 0

  return {
    'dh': dh if dh is not None else defaults[DenavitHartenberg],
    'limits': limits if limits is not None else defaults[JointLimits],
    'home': home if home is not None else defaults['home']
  }

class TestJoint(unittest.TestCase):
  def setUp(self):
    dh     = DenavitHartenberg(math.radians(45), 50, math.radians( 180), 72)
    limits = JointLimits(math.radians(400), math.radians(-400))
    home   = math.radians(45)
    self.joint = Joint(dh, limits, home)

  def test_init_swaps_limits(self):
    expected = JointLimits(math.radians(-400), math.radians(400))

    for component in self.joint.limits._fields:
      self.assertEqual(getattr(self.joint.limits, component), getattr(expected, component))

  def test_joint_angle_defaults_to_home_value(self):
    self.assertEqual(self.joint.angle, self.joint.home)

  def test_joint_home_defaults_to_zero(self):
    d = create_dummy_dict()

    del d['home']
    joint = Joint.from_dict(d)

    self.assertAlmostEqual(joint.home, 0)

  def test_init_home_defaults_to_lower_limit_if_home_is_outside_joint_limits(self):
    d = create_dummy_dict(home = 100)

    joint = Joint.from_dict(d)

    self.assertAlmostEqual(joint.home, joint.limits.low)

  def test_immovable_is_identity_transform(self):
    joint = Joint.Immovable()

    self.assertEqual(joint.transform.dual, Transform.Identity().dual)

  def test_from_dict_converts_degrees_to_radians(self):
    d = create_dummy_dict()

    joint = Joint.from_dict(d)

    self.assertAlmostEqual(joint.dh.alpha,    math.radians(d['dh']['alpha']))
    self.assertAlmostEqual(joint.dh.theta,    math.radians(d['dh']['theta']))
    self.assertAlmostEqual(joint.limits.low,  math.radians(d['limits']['low']))
    self.assertAlmostEqual(joint.limits.high, math.radians(d['limits']['high']))
    self.assertAlmostEqual(joint.home,        math.radians(d['home']))

  def test_from_dict_raises_on_missing_dh_key(self):
    fields = self.joint.dh._fields

    for field in fields:
      with self.subTest(msg=f'Remove `{field}` from dictionary'):
        d = create_dummy_dict()
        del d['dh'][field]

        with self.assertRaises(InvalidJointDictError):
          Joint.from_dict(d)

  def test_from_dict_handles_limits_key(self):
    TestSpec = namedtuple('TestSpec', 'name input_dict')

    tests = [
      TestSpec("No limits", {}),
      TestSpec("Low only", { 'low': 10 }),
      TestSpec("High only", { 'high': 20 }),
      TestSpec("Both limits", { 'low': 10, 'high': 20 }),
      TestSpec("Junk limits", { 'Junk': 'Limits' })
    ]

    defaults = { 'low': -math.inf, 'high': math.inf }

    for test in tests:
      d = create_dummy_dict(limits=test.input_dict)

      joint = Joint.from_dict(d)

      expecteds = {
        **defaults,
        **{
          k: math.radians(v)
          for k, v in test.input_dict.items()
          if k in JointLimits._fields
        }
      }

      for field in JointLimits._fields:
        with self.subTest(msg=f"{test.name}: `{field}` not as expected"):
          self.assertEqual(getattr(joint.limits, field), expecteds.get(field))

  def test_set_angle_set_valid_angles_and_raises_for_exceeding_limits(self):
    with self.subTest(f"Valid angle is accepted"):
      valid_angle = (self.joint.limits.high + self.joint.limits.low) / 2

      self.joint.set_angle(valid_angle)
      self.assertAlmostEqual(self.joint.angle, valid_angle)

    with self.subTest(f"Invalid angle raises exception"):
      invalid_angle = self.joint.limits.high + abs(self.joint.limits.low)

      with self.assertRaises(InvalidJointAngleError):
        self.joint.set_angle(invalid_angle)

  def test_set_angle_accepts_normalized_values(self):
    valid_angles = [0, 0.5, 1]
    for valid_angle in valid_angles:
      with self.subTest(f'Valid value {valid_angle}'):
        self.joint.set_angle(valid_angle, normalized=True)
        normalized = valid_angle * self.joint.travel + self.joint.limits.low
        self.assertAlmostEqual(self.joint.angle, normalized)

    invalid_angles = [-1, 2]
    for invalid_angle in invalid_angles:
      with self.subTest(f'Invalid angle {invalid_angle}'):
        with self.assertRaises(AssertionError):
          self.joint.set_angle(invalid_angle, normalized=True)

  def test_normalized_angle_returns_value_between_zero_and_one(self):
    angles = [
      (self.joint.limits.low,  0),
      (self.joint.limits.high, 1),
      (self.joint.travel / 4 + self.joint.limits.low, 0.25),
    ]

    for angle, normalized_angle in angles:
      with self.subTest(f'Angle {math.degrees(angle)}'):
        self.joint.set_angle(angle)
        self.assertAlmostEqual(normalized_angle, self.joint.normalized_angle)


  def test_transform_constructs_transform_for_joint_angle(self):
    self.joint.angle = math.radians(30)

    theta = Transform.from_axis_angle_translation(axis = Vector3.Z(), angle = self.joint.dh.theta + self.joint.angle)
    alpha = Transform.from_axis_angle_translation(axis = Vector3.X(), angle = self.joint.dh.alpha)
    d     = Transform.from_axis_angle_translation(translation = Vector3(0, 0, self.joint.dh.d))
    a     = Transform.from_axis_angle_translation(translation = Vector3(self.joint.dh.a, 0, 0))

    expected = d * theta * a * alpha

    self.assertAlmostEqual(self.joint.transform.dual, expected.dual)

  def test_travel_returns_amount_of_travel_between_limits(self):
    expected = self.joint.limits.high - self.joint.limits.low

    self.assertAlmostEqual(self.joint.travel, expected)

  def test_travel_in_revs_returns_amount_of_travel_in_integer_revolutions(self):
    expected = math.floor((self.joint.limits.high - self.joint.limits.low) / (2 * math.pi))

    self.assertEqual(self.joint.travel_in_revs, expected)

  def test_within_limits_checks_floating_point_angles(self):
    # Generate an angle guaranteed to be inside joint limits
    inside = (self.joint.limits.high - self.joint.limits.low) / 2
    self.assertTrue(self.joint.within_limits(inside))

    # Generate an angle guaranteed to be outside joint limits
    outside = (self.joint.limits.high + abs(self.joint.limits.low))
    self.assertFalse(self.joint.within_limits(outside))

  def test_within_limits_returns_true_for_singular_values(self):
    # Useful for checking limits on the inverse kinematic results
    # Some axes will have singular solutions (meaning infinitely many)
    # So clearly the solution should be considered within limits
    self.assertTrue(self.joint.within_limits(constant.SINGULAR))
