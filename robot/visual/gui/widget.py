from robot.spatial import Vector3

class Widget():
  """Base class for all GUI objects."""
  def __init__(self, **options: dict) -> None:
    self.name  = options.get('name', None)
    self.color = options.get('color', [1, 1, 1])
    self.hover = False

    # Parent dependent properties; all use a getter and setter
    self._position = options.get('position', Vector3())
    self._width    = options.get('width', 1.0)
    self._height   = options.get('height', 1.0)
    self._visible  = options.get('visible', True)

    self.parent   = None
    self.children = {}

  def add(self, widget: 'Widget') -> None:
    """Add a child Widget."""
    assert isinstance(widget, Widget), "Child must be a (subclass of) Widget"

    widget.parent = self
    self.children[widget.name] = widget

  @property
  def width(self) -> float:
    """Width of Widget as a percentage of the screen size."""
    width = self._width
    if self.parent is not None:
      width *= self.parent.width

    assert width >= 0

    return width

  @width.setter
  def width(self, width: float) -> None:
    self._width = width

  @property
  def height(self) -> float:
    """Height of Widget as a percentage of the screen size."""
    height = self._height
    if self.parent is not None:
      height *= self.parent.height

    assert height >= 0

    return height

  @height.setter
  def height(self, height: float) -> None:
    self._height = height

  @property
  def position(self) -> Vector3:
    """Absolute position of top left corner of Widget."""
    if self.parent is not None:
      world_position = Vector3(self._position.x * self.parent.width, self._position.y * self.parent.height)
      return world_position + self.parent.position
    else:
      return self._position

  @position.setter
  def position(self, position: Vector3) -> None:
    self._position = position

  @property
  def visible(self) -> bool:
    if self.parent is not None:
      return self._visible and self.parent.visible
    else:
      return self._visible

  @visible.setter
  def visible(self, visible: bool) -> None:
    self._visible = visible

  def click(self, *args) -> None:
    self.propagate_click(*args)

  def drag(self, *args) -> None:
    self.propagate_drag(*args)

  def cursor(self, *args) -> None:
    self.propagate_cursor(*args)

  def propagate_click(self, button, action, cursor, mods) -> None:
    for child in self.children.values():
      if child.contains(cursor):
        if hasattr(child, 'click'):
          child.click(button, action, cursor, mods)

  def propagate_drag(self, button, cursor, cursor_delta, modifiers) -> None:
    for child in self.children.values():
      if child.contains(cursor):
        if hasattr(child, 'drag'):
          child.drag(button, cursor, cursor_delta, modifiers)

  def propagate_cursor(self, button, cursor, cursor_delta, modifiers) -> None:
    for child in self.children.values():
      if child.contains(cursor):
        if hasattr(child, 'cursor'):
          child.cursor(button, cursor, cursor_delta, modifiers)

  def contains(self, point: Vector3) -> bool:
    """Return True if the point is inside the Widget."""
    inside_x = self.position.x <= point.x <= (self.position.x + self.width)
    inside_y = self.position.y <= point.y <= (self.position.y + self.height)

    return inside_x and inside_y