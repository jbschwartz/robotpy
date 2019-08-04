import math, unittest
from operator import itemgetter

from robot.spatial import euler, Quaternion

class TestEuler(unittest.TestCase):
  def setUp(self):
    # Frame is constructed by rotating around Z 45 degrees, rotation around new Y 135 degrees
    self.q = Quaternion(0.353553, -0.353553, 0.853553, 0.146447)

  def checkSolutions(self, results, solutions):
    results.sort(key = itemgetter(1), reverse = True)
    solutions.sort(key = itemgetter(1), reverse = True)

    for index, (result, expecteds) in enumerate(zip(results, solutions)):
      for angleIndex, (angle, expected) in enumerate(zip(result, expecteds)):
        with self.subTest(f"Solution #{index+1}, Angle #{angleIndex+1}"):
          self.assertAlmostEqual(angle, expected, places=5)

  def test_zyx(self):
    results = euler.zyx(*self.q)
    solutions = [ [math.radians(-135), math.radians(45), math.radians(180)], [math.radians(45), math.radians(225), math.radians(0)] ]

    self.checkSolutions(results, solutions)

  def test_zyz(self):
    results = euler.zyz(*self.q)
    solutions = [ [math.radians(45), math.radians(135), math.radians(0)], [math.radians(-135), math.radians(-135), math.radians(-180)] ]

    self.checkSolutions(results, solutions)