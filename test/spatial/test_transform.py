import unittest
import math

from robot.spatial import Quaternion, Transform, Vector3
import robot.spatial.quaternion as quaternion

class TestTransform(unittest.TestCase):
  def setUp(self):
    self.pureTranslate = Transform(translation = Vector3(4, 2, 6))
    self.pureRotate = Transform(axis = Vector3(1, 0, 0), angle = math.radians(180))
    self.both = Transform(axis = Vector3(1, 0, 0), angle = math.radians(180), translation = Vector3(4, 2, 6))
    self.point = Vector3(3, 4, 5)

  def test_init(self):
    '''
    Transform accepts ...
    '''
    pass

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