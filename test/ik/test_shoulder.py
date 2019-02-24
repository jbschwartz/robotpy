import unittest
import math

from robot import ik

class TestShoulder(unittest.TestCase):
  def setUp(self):
    self.upperArmLength = 10
    self.foreArmLength = 5

    self.theta = [ math.radians(10), math.radians(45) ]

    self.x = self.upperArmLength * math.cos(self.theta[0]) + self.foreArmLength * math.cos(self.theta[0] + self.theta[1])
    self.y = self.upperArmLength * math.sin(self.theta[0]) + self.foreArmLength * math.sin(self.theta[0] + self.theta[1])

  def test_shoulder(self):
    '''
    Solve for the shoulder angle
    '''

    # For points on external workspace boundary
    fullReach = self.upperArmLength + self.foreArmLength
    elbow = ik.solve_elbow(fullReach, 0, self.upperArmLength, self.foreArmLength)
    result = ik.solve_shoulder(fullReach, 0, self.upperArmLength, self.foreArmLength, elbow)
    expected = 0
    
    self.assertEqual(len(result), 1)
    self.assertAlmostEqual(result[0], expected)

    # For points on internal workspace boundary
    internalBoundary = self.upperArmLength - self.foreArmLength
    elbow = ik.solve_elbow(internalBoundary, 0, self.upperArmLength, self.foreArmLength)
    result = ik.solve_shoulder(internalBoundary, 0, self.upperArmLength, self.foreArmLength, elbow)
    expected = 0

    self.assertEqual(len(result), 1)
    self.assertAlmostEqual(result[0], expected)

    # For a position in the workspace
    elbow = ik.solve_elbow(self.x, self.y, self.upperArmLength, self.foreArmLength)
    results = ik.solve_shoulder(self.x, self.y, self.upperArmLength, self.foreArmLength, elbow)
    expecteds = [ self.theta[0], 2 * math.atan2(self.y, self.x) - self.theta[0] ]

    self.assertEqual(len(results), 2)
    for result, expected in zip(results, expecteds):
      with self.subTest(msg="For a position in the workspace"):
        self.assertAlmostEqual(result, expected)

    # For the origin (i.e. on the shoulder axis)
    elbow = ik.solve_elbow(0, 0, self.upperArmLength, self.upperArmLength)
    result = ik.solve_shoulder(0, 0, self.upperArmLength, self.upperArmLength, elbow)
    expected = math.inf

    self.assertEqual(len(result), 1)
    self.assertEqual(result[0], expected)
    

