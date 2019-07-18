import math, unittest

from robot.spatial.dual       import Dual
from robot.spatial.frame      import Frame
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform
from robot.spatial.vector3    import Vector3

class TestFrame(unittest.TestCase):
  def setUp(self):
    # Default Frame
    self.f0 = Frame()

    # Frame is constructed by rotating around Z 45 degrees, rotation around new Y 135 degrees
    self.f1 = Frame(Transform(dual = Dual(
      Quaternion(0.353553, -0.353553, 0.853553, 0.146447),
      Quaternion(0, 0, 0, 0)
    )))

    self.t = Transform(axis = Vector3(0, 0, 1), angle = math.radians(45))
    self.f2 = Frame(self.t)

  def test_init(self):
    # Default frame is expected to be a standard XYZ coordinate frame
    expected = Vector3(1, 0, 0)
    self.assertEqual(self.f0.x(), expected)

    expected = Vector3(0, 1, 0)
    self.assertEqual(self.f0.y(), expected)

    expected = Vector3(0, 0, 1)
    self.assertEqual(self.f0.z(), expected)

  def test_rmul(self):
    transform = Transform(axis = Vector3(1, 0, 0), angle = math.radians(90), translation = Vector3(0, 0, 100))

    new_frame = transform * self.f0

    expected = Vector3(1, 0, 0)
    self.assertAlmostEqual(new_frame.x(), expected)

    expected = Vector3(0, 0, 1)
    self.assertAlmostEqual(new_frame.y(), expected)

    expected = Vector3(0, -1, 0)
    self.assertAlmostEqual(new_frame.z(), expected)

    expected = Vector3(0, 0, 100)
    self.assertAlmostEqual(new_frame.position(), expected)

  def test_x(self):
    expected = self.t(Vector3(1, 0, 0))
    self.assertEqual(self.f2.x(), expected)

  def test_y(self):
    expected = self.t(Vector3(0, 1, 0))
    self.assertEqual(self.f2.y(), expected)

  def test_z(self):
    expected = self.t(Vector3(0, 0, 1))
    self.assertEqual(self.f2.z(), expected)

