import math, unittest

from robot.mech        import Joint, Serial
from robot.mech.robots import ABB_IRB_120
from robot.spatial     import Vector3

class TestSerial(unittest.TestCase):
  def setUp(self):
    self.robot = ABB_IRB_120

  def test_pose(self):
    angles = [ math.radians(45) ] * 6
    self.robot.angles = angles
    frame = self.robot.pose()

    result = frame.translation()
    expected = Vector3(133.58578643, 184.49747468, 128.00714267)

    self.assertAlmostEqual(result, expected)

  def test_poses(self):
    angles = [ math.radians(0) ] * 6
    self.robot.angles = angles
    frames = self.robot.poses()
    expecteds = [
      Vector3(0, 0, 0),
      Vector3(0, 0, 290),
      Vector3(0, 0, 560),
      Vector3(0, 0, 630),
      Vector3(302, 0, 630),
      Vector3(302, 0, 630),
      Vector3(374, 0, 630)
    ]

    for index, (frame, expected) in enumerate(zip(frames, expecteds)):
      with self.subTest(f"Frame #{index + 1}"):
        result = frame.translation()
        self.assertAlmostEqual(result, expected)

  def test_transform_to_robot(self):
    # The last argument accounts for the elbow offset to the wrist
    results = [[ math.radians(45), 0, math.atan(70 / 302) ]]
    solutions = [[ math.radians(45), math.radians(90), math.radians(-90) ]]

    self.robot.transform_to_robot(results)

    for result, expecteds in zip(results, solutions):
      for angle, expected in zip(result, expecteds):
        self.assertAlmostEqual(angle, expected)

  def test_wrist_center(self):
    angles = [ math.radians(45) ] * 6
    self.robot.angles = angles
    frame = self.robot.pose()

    result = self.robot.wrist_center(frame)
    expected = Vector3(184.49747468, 184.49747468, 178.91883092)

    self.assertAlmostEqual(result, expected)



