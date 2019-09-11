import math, unittest

from robot.visual.gui.animation import Animation

class TestAnimation(unittest.TestCase):
  def setUp(self):
    self.animation = Animation(1)

  def test_animation_is_done_on_initialization(self):
    self.assertTrue(self.animation.is_done)

  def test_animation_is_not_done_after_reset(self):
    self.animation.reset()
    self.assertFalse(self.animation.is_done)

  def test_reverse_switches_the_start_and_stop_keys(self):
    self.animation.set_end_points(0, 1)
    self.animation.reverse()

    self.assertEqual(self.animation.start, 1)
    self.assertEqual(self.animation.stop, 0)