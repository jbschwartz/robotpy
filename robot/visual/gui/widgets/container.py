from robot.spatial                      import Vector3
from robot.visual.gui.widget            import Widget
from robot.visual.gui.widgets.rectangle import Rectangle

class Container(Widget):
  def __init__(self, **options):
    super().__init__(**options)

  def layout(self, top: int, right: int, bottom: int, left: int):
    max_width = 0
    current_y = 0
    for child in self.children.values():
      if hasattr(child, 'fixed_size') and child.fixed_size:
        current_y += top
        child.fixed_position = Vector3(left, current_y)
        max_width = max(max_width, child.fixed_width)
        current_y += child.fixed_height + bottom

    self.fixed_width = max_width + left + right
    self.fixed_height = current_y