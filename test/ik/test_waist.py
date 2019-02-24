import unittest
import math

from robot import ik, utils

class TestWaist(unittest.TestCase):
  def setUp(self):
    self.angles = [ 0, 30, 90, 150, -120, -90, -30 ]
    self.alphas = [ 0, 15, -15 ]
    self.armLength = 3

  def test_waist(self):
    '''
    Solve for the waist angle with and without a shoulder offset
    '''
    for alpha in self.alphas:
      with self.subTest(alpha=alpha): 
        # Prescribe the alpha angle and solve for shoulderOffset
        # This makes the expected results easy to reason about
        alpha = math.radians(alpha)
        shoulderOffset = self.armLength * math.sin(alpha)

        for angle in self.angles: 
          angle = math.radians(angle)
          # Calculate target position
          y = self.armLength * math.sin(angle)
          x = self.armLength * math.cos(angle)

          results = ik.solve_waist(x, y, shoulderOffset)
          expecteds = [ utils.clampAngle(angle - alpha), utils.clampAngle(angle + alpha + math.pi) ]
          
          for result, expected in zip(results, expecteds):
            with self.subTest(angle=angle):
              self.assertAlmostEqual(result, expected)
    
    # Determine the singular position
    expected = math.inf
    self.assertEqual(ik.solve_waist(0, 0)[0], expected)

