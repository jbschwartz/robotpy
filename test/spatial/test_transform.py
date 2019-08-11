import math, unittest

from robot.spatial       import Quaternion, Transform, Vector3
from robot.spatial.euler import Axes, Order

class TestTransform(unittest.TestCase):
  def setUp(self):
    self.pureTranslate = Transform.from_axis_angle_translation(translation = Vector3(4, 2, 6))
    self.pureRotate = Transform.from_axis_angle_translation(axis = Vector3.X(), angle = math.radians(180))
    self.both = Transform.from_axis_angle_translation(axis = Vector3.X(), angle = math.radians(180), translation = Vector3(4, 2, 6))
    self.point = Vector3(3, 4, 5)

  def test_init(self):
    '''
    Transform accepts ...
    '''
    pass

  def test_from_json(self):
    translation = [1, 2, 3]
    angles      = [-30, 60, 90]
    axes        = 'ZYZ'
    order       = 'INTRINSIC'

    payload = {
      'translation': translation,
      'euler': {
        'angles': angles,
        'axes': axes,
        'order': order
      }
    }

    expected = Transform.from_orientation_translation(
      Quaternion.from_euler(
        list(map(math.radians, angles)),
        Axes[axes],
        Order[order]
      ),
      Vector3(*translation)
    )

    result = Transform.from_json(payload)

    self.assertAlmostEqual(result.dual, expected.dual)

  def test_from_json_raises(self):
    failed_payload = {
      'translation': [1, 2, 3],
      'euler': {
        'angles': [-30, 60, 90],
        'axes': 'ZZZ',
        'order': 'SIC'
      }
    }

    with self.assertRaises(KeyError):
      _ = Transform.from_json(failed_payload)

    del failed_payload['translation']

    with self.assertRaises(KeyError):
      _ = Transform.from_json(failed_payload)

  def test_mul(self):
    # Rotate then translate
    combined = self.pureTranslate * self.pureRotate
    result = combined(self.point)
    expected = self.pureTranslate(self.pureRotate(self.point)) # Vector3(7, -2, 1)

    self.assertAlmostEqual(result.x, expected.x)
    self.assertAlmostEqual(result.y, expected.y)
    self.assertAlmostEqual(result.z, expected.z)

    # Translate then rotate
    combined = self.pureRotate * self.pureTranslate
    result = combined(self.point)
    expected = self.pureRotate(self.pureTranslate(self.point)) # Vector3(7, -6, -11)

    self.assertAlmostEqual(result.x, expected.x)
    self.assertAlmostEqual(result.y, expected.y)
    self.assertAlmostEqual(result.z, expected.z)

  def test_call(self):
    # Pure translation
    expected = Vector3(7, 6, 11)
    self.assertEqual(self.pureTranslate(self.point), expected)

    # Pure rotation
    expected = Vector3(3, -4, -5)
    self.assertEqual(self.pureRotate(self.point), expected)

    # Rotation and translation (in that order)
    result = self.both(self.point)
    expected = Vector3(7, -2, 1)

    self.assertAlmostEqual(result.x, expected.x)
    self.assertAlmostEqual(result.y, expected.y)
    self.assertAlmostEqual(result.z, expected.z)

  def test_translation(self):
    expected = Vector3(4, 2, 6)
    self.assertEqual(self.pureTranslate.translation(), expected)

  def test_rotation(self):
    expected = self.pureRotate.dual.r
    self.assertEqual(self.pureRotate.rotation(), expected)

  def test_inverse(self):
    expected = self.point

    inverse = self.both.inverse()
    self.assertAlmostEqual(inverse(self.both(self.point)), expected)