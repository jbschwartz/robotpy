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

    self._is_clicked = False

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

  @property
  def is_clicked(self) -> bool:
    return self._is_clicked

  @is_clicked.setter
  def is_clicked(self, is_clicked: bool) -> None:
    self._is_clicked = is_clicked

    if self.parent is not None:
      self.parent.is_clicked = self._is_clicked

  def click(self, *args) -> None:
    cursor = args[2]
    self.propagate('click', cursor, *args)

  def drag(self, *args) -> None:
    cursor = args[1]
    self.propagate('drag', cursor, *args)

  def cursor(self, *args) -> None:
    cursor = args[1]
    self.propagate('cursor', cursor, *args)

  def update(self, delta: float) -> None:
    for child in self.children.values():
      update_fn = getattr(child, 'update', None)
      if update_fn is not None:
        update_fn(delta)

  def propagate(self, event, cursor, *args):
    for child in self.children.values():
      if child.contains(cursor) or child.is_clicked:
        if hasattr(child, event):
          fn = getattr(child, event)
          fn(*args)

  def contains(self, point: Vector3) -> bool:
    """Return True if the point is inside the Widget."""
    inside_x = self.position.x <= point.x <= (self.position.x + self.width)
    inside_y = self.position.y <= point.y <= (self.position.y + self.height)

    return inside_x and inside_y