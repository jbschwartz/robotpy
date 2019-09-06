import math, unittest

from robot.spatial     import Vector3
from robot.visual.gui  import Widget

class TestWidget(unittest.TestCase):
  def setUp(self):
    self.parent       = Widget('Parent')
    self.child        = Widget('Child')
    self.grand_child  = Widget('Grand Child')

  def test_widget_defaults_to_full_size(self):
    default = Widget('Default')

    self.assertAlmostEqual(default.position, Vector3())
    self.assertEqual(default.width,  1.)
    self.assertEqual(default.height, 1.)

  def test_widget_adds_child_with_name_as_key(self):
    self.parent.add(self.child)

    self.assertIs(self.parent.children[self.child.name], self.child)

  def test_widget_adds_child_assigns_parent(self):
    self.parent.add(self.child)

    self.assertIs(self.parent, self.child.parent)

  def test_widget_moves_children_with_it(self):
    self.parent.add(self.child)
    self.parent.position = Vector3(0.5, 0.5)

    with self.subTest('Child'):
      self.assertAlmostEqual(self.parent.position, self.child.position)

    with self.subTest('Grand Child'):
      self.child.add(self.grand_child)
      self.assertAlmostEqual(self.parent.position, self.grand_child.position)

  def test_widget_scales_children_with_it(self):
    self.parent.add(self.child)
    self.parent.height = 0.5
    self.parent.width  = 0.5

    with self.subTest('Child'):
      with self.subTest('Height'):
        self.assertAlmostEqual(self.parent.height, self.child.height)

      with self.subTest('Width'):
        self.assertAlmostEqual(self.parent.width, self.child.width)

    with self.subTest('Grand Child'):
      self.child.add(self.grand_child)

      with self.subTest('Height'):
        self.assertAlmostEqual(self.parent.height, self.grand_child.height)

      with self.subTest('Width'):
        self.assertAlmostEqual(self.parent.width, self.grand_child.width)

  def test_widget_contains_returns_true_for_points_inside(self):
    w = Widget('Widget', Vector3(), 0.5, 0.5)

    test_points = [
      (Vector3(0, 0),       True),
      (Vector3(0.25, 0.25), True),
      (Vector3(0.25, 0.75), False),
      (Vector3(-1, 1),      False),
    ]

    for point, expected in test_points:
      self.assertEqual(expected, w.contains(point))