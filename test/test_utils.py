import unittest
import math

from robot import utils 

class TestUtils(unittest.TestCase):
  def setUp(self):
    pass

  def test_clampAngle(self):
    angle = math.radians(400)
    expected = math.radians(40)
    self.assertAlmostEqual(utils.clampAngle(angle), expected)

    angle = math.radians(-400)
    expected = math.radians(-40)
    self.assertAlmostEqual(utils.clampAngle(angle), expected)

    angle = math.radians(-180)
    expected = math.radians(180)
    self.assertAlmostEqual(utils.clampAngle(angle), expected)