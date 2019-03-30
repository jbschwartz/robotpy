import unittest
import math
from operator import itemgetter

from robot import ik
from robot.mech.robots import ABB_IRB_120

class TestAngles(unittest.TestCase):
  def setUp(self):
    self.ABB_IRB_120 = ABB_IRB_120

    self.angles = [ math.radians(45) ] * 6

  def test_angles(self):
    angle = math.radians(45)

    solutions = [
      [angle, angle, angle, angle, angle, angle],
      [angle, angle, angle, -math.radians(135), -angle, -math.radians(135)],
      [angle, angle, angle, angle, angle, math.radians(-315)],
      [angle, angle, angle, -math.radians(135), -angle, math.radians(225)],
    ]

    self.ABB_IRB_120.qs = solutions[0]
    f = self.ABB_IRB_120.pose()

    results = ik.solve_angles(f, self.ABB_IRB_120)

    solutions.sort(key = itemgetter(0, 3, 5))
    results.sort(key = itemgetter(0, 3, 5))

    for index, (result, expecteds) in enumerate(zip(results, solutions)):
      for joint, (angle, expected) in enumerate(zip(result, expecteds)):
        with self.subTest(msg=f"Result #{index}, Joint #{joint + 1}"):
          self.assertAlmostEqual(angle, expected)