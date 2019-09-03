from robot.spatial import Vector3

class Widget():
  """Base class for all GUI objects."""
  def __init__(self, name: str, position: Vector3 = None, width: float = 1, height: float = 1) -> None:
    self.name      = name
    self._position = position or Vector3()
    self._width    = width
    self._height   = height

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

  def contains(self, point: Vector3) -> bool:
    """Return True if the point is inside the Widget."""
    inside_x = self.position.x <= point.x <= (self.position.x + self.width)
    inside_y = self.position.y <= point.y <= (self.position.y + self.height)

    return inside_x and inside_y