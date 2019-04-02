import math, unittest

from robot.traj.linear_js import LinearJS

class TestLinearJS(unittest.TestCase):
  def setUp(self):
    self.starts = [0] * 6
    self.ends = [math.radians(45)] * 6
    self.duration = 10

    self.traj = LinearJS(self.starts, self.ends, self.duration)
    
  def test_advance(self):
    expecteds = [math.radians(4.5)] * 6
    results = self.traj.advance(1)

    [self.assertAlmostEqual(result, expected) for result, expected in zip(results, expecteds)]

  def test_advance_beyond_end(self):
    expecteds = self.ends
    results =  self.traj.advance(self.duration + 1)

    [self.assertAlmostEqual(result, expected) for result, expected in zip(results, expecteds)]

  @unittest.skip('Implement test')
  def test_is_done(self):
    expected = False
    self.assertEqual(self.traj.is_done(), expected)

    self.traj.advance(0.5)
    self.assertEqual(self.traj.is_done(), expected)

    self.traj.advance(10)
    expected = True
    self.assertEqual(self.traj.is_done(), expected)