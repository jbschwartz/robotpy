import math, unittest

import robot.ik    as ik
import robot.utils as utils
from robot.spatial.vector3 import Vector3

class TestArm(unittest.TestCase):
  def setUp(self):
    # TODO: Try this with some non-zero joint angles (and not on the workspace boundary)
    self.target = Vector3(10, 25, 10)

    self.upperArmLength = 15
    self.foreArmLength = 10
    self.shoulderWristOffset = 10
    self.shoulderZ = 20

  def test_arm(self):
    waistAngles = ik.solve_waist(self.target.x, self.target.y, self.shoulderWristOffset)
    expectedSets = [ [waistAngles[0], math.radians(0), 0], [waistAngles[1], math.radians(180), 0] ]
    resultSets = ik.solve_arm(self.target, self.upperArmLength, self.foreArmLength, self.shoulderWristOffset, self.shoulderZ)

    for resultSet, expectedSet in zip(resultSets, expectedSets):
      with self.subTest():
        for angle, expected in zip(resultSet, expectedSet):
          self.assertAlmostEqual(angle, expected)