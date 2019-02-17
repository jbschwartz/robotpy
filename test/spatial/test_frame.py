import unittest
import math

from robot.spatial import Dual, Frame, Quaternion, Transform, Vector3

class TestFrame(unittest.TestCase):
  def setUp(self):
    # Default Frame
    self.f0 = Frame()

    # Frame is constructed by rotating around Z 45 degrees, rotation around new Y 135 degrees
    self.f1 = Frame(Dual(
      Quaternion(0.353553, -0.353553, 0.853553, 0.146447),
      Quaternion(0, 0, 0, 0)
    ))

    self.t = Transform(axis = Vector3(0, 0, 1), angle = math.radians(45))
    self.f2 = Frame(self.t.dual)

  def test_init(self):
    # Default frame is expected to be a standard XYZ coordinate frame
    expected = Vector3(1, 0, 0)
    self.assertEqual(self.f0.x(), expected)

    expected = Vector3(0, 1, 0)
    self.assertEqual(self.f0.y(), expected)

    expected = Vector3(0, 0, 1)
    self.assertEqual(self.f0.z(), expected)

  def test_euler(self):
    # Default method and order should be intrinsic ZYX
    result = self.f1.euler()
    expecteds = [ math.radians(-135), math.radians(45), math.radians(180) ]

    for angle, expected in zip(result, expecteds):
      self.assertAlmostEqual(angle, expected, places=5)

    methods = ["intrinsic", "extrinsic"]
    orders = ["ZYX", "ZYZ"]
    expecteds = {
      "intrinsicZYX": [ math.radians(-135), math.radians(45), math.radians(180) ],
      "intrinsicZYZ": [ math.radians(45), math.radians(135), math.radians(0) ],
      "extrinsicXYZ": [ math.radians(180), math.radians(45), math.radians(-135) ],
      "extrinsicZYZ": [ math.radians(0), math.radians(135), math.radians(45) ]
    }

    for method in methods:
      for order in orders:

        if method == "extrinsic":
          order = order[::-1]

        result = self.f1.euler(method=method, order=order)
        for angle, expected in zip(result, expecteds[method + order]):
          with self.subTest(f"{method}, {order}"):
            self.assertAlmostEqual(angle, expected, places=5)

  def test_x(self):
    expected = self.t.apply(Vector3(1, 0, 0))
    self.assertEqual(self.f2.x(), expected)

  def test_y(self):
    expected = self.t.apply(Vector3(0, 1, 0))
    self.assertEqual(self.f2.y(), expected)

  def test_z(self):
    expected = self.t.apply(Vector3(0, 0, 1))
    self.assertEqual(self.f2.z(), expected)

