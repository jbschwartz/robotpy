import math, unittest

from collections import namedtuple

from robot.mech.joint        import DenavitHartenberg, JointLimits, Joint
from robot.spatial.vector3   import Vector3
from robot.spatial.transform import Transform

def create_dummy_dict(dh: dict = None, limits: dict = None):
  """Create a sample dictionary with all of the DH fields present."""
  defaults = {
    tup: {k: v for k, v in zip(tup._fields, range(0, len(tup._fields)))}
    for tup in (DenavitHartenberg, JointLimits)
  }

  return {
    'dh': dh if dh is not None else defaults[DenavitHartenberg],
    'limits': limits if limits is not None else defaults[JointLimits]
  }

class TestJoint(unittest.TestCase):
  def setUp(self):
    dh     = DenavitHartenberg(math.radians(45), 50, math.radians( 180), 72)
    limits = JointLimits(math.radians(400), math.radians(-400))
    self.joint = Joint(dh, limits)

  def test_init_swaps_limits(self):
    expected = JointLimits(math.radians(-400), math.radians(400))

    for component in self.joint.limits._fields:
      self.assertEqual(getattr(self.joint.limits, component), getattr(expected, component))

  def test_from_dict_raises_on_missing_dh_key(self):
    fields = self.joint.dh._fields

    for field in fields:
      with self.subTest(msg=f'Remove `{field}` from dictionary'):
        d = create_dummy_dict()
        del d['dh'][field]

        with self.assertRaises(KeyError):
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

  def test_transform(self):
    self.joint.angle = math.radians(30)

    theta = Transform.from_axis_angle_translation(axis = Vector3(0, 0, 1), angle = self.joint.dh.theta + self.joint.angle)
    alpha = Transform.from_axis_angle_translation(axis = Vector3(1, 0, 0), angle = self.joint.dh.alpha)
    d     = Transform.from_axis_angle_translation(translation = Vector3(0, 0, self.joint.dh.d))
    a     = Transform.from_axis_angle_translation(translation = Vector3(self.joint.dh.a, 0, 0))

    expected = d * theta * a * alpha

    self.assertAlmostEqual(self.joint.transform.dual, expected.dual)

  def test_travel_returns_amount_of_travel_between_limits(self):
    expected = self.joint.limits.high - self.joint.limits.low

    self.assertAlmostEqual(self.joint.travel, expected)

  def test_travel_in_revs_returns_amount_of_travel_in_integer_revolutions(self):
    expected = math.floor((self.joint.limits.high - self.joint.limits.low) / (2 * math.pi))

    self.assertEqual(self.joint.travel_in_revs(), expected)
