import math, unittest

from robot import ik, utils

class TestElbow(unittest.TestCase):
  def setUp(self):
    self.upperArmLength = 10
    self.foreArmLength = 5

  def test_elbow(self):
    '''
    Solve for the elbow angle
    '''

    # For points out of reach
    outOfReach = self.upperArmLength + self.foreArmLength
    result = ik.solve_elbow(outOfReach, outOfReach, self.upperArmLength, self.foreArmLength)

    self.assertTrue(math.isnan(result))

    # For points too close to reach
    outOfReach = 0
    result = ik.solve_elbow(outOfReach, outOfReach, self.upperArmLength, self.foreArmLength)

    self.assertTrue(math.isnan(result))

    # For points on external workspace boundary
    fullReach = self.upperArmLength + self.foreArmLength
    result = ik.solve_elbow(fullReach, 0, self.upperArmLength, self.foreArmLength)
    expected = 0
    
    self.assertAlmostEqual(result, expected)

    # For points on internal workspace boundary
    internalBoundary = self.upperArmLength - self.foreArmLength
    result = ik.solve_elbow(internalBoundary, 0, self.upperArmLength, self.foreArmLength)
    expected = math.pi
    
    self.assertAlmostEqual(result, expected)

    # For the origin (i.e. on the shoulder axis)
    result = ik.solve_elbow(0, 0, self.upperArmLength, self.upperArmLength)
    expected = math.pi

    self.assertAlmostEqual(result, expected)
    
    # For a position in the workspace

    # Construct a 2R manipulator in the plane so the expected result is prescribed
    #  i.e. complete forward kinematics first so we know what to expect from inverse kinematics
    theta = [ math.radians(10), math.radians(45) ]

    x = self.upperArmLength * math.cos(theta[0]) + self.foreArmLength * math.cos(theta[0] + theta[1])
    y = self.upperArmLength * math.sin(theta[0]) + self.foreArmLength * math.sin(theta[0] + theta[1])

    result = ik.solve_elbow(x, y, self.upperArmLength, self.foreArmLength)

    expected = theta[1]

    self.assertAlmostEqual(result, expected)