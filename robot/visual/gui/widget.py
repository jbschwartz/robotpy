from typing import Iterable

from robot.spatial import Vector3
from robot.visual.messaging.event import Event

class Widget():
  """Base class for all GUI objects."""
  def __init__(self, **options: dict) -> None:
    self.name  = options.get('name', None)
    self.color = options.get('color', [1, 1, 1])
    self.hover = False
    self.fixed_size = options.get('fixed_size', False)

    if self.fixed_size:
      self.fixed_width = options.get('width', 100)
      self.fixed_height = options.get('height', 100)
      self.fixed_position = options.get('position', Vector3())
    else:
      # Parent dependent properties; all use a getter and setter
      self._width    = options.get('width', 1.0)
      self._height   = options.get('height', 1.0)
      self._position = options.get('position', Vector3())

    self._visible  = options.get('visible', True)

    self._is_clicked = False

    self.parent   = None
    self.children = {}

  def add(self, *widgets: 'Widget') -> None:
    """Add child Widgets."""
    for widget in widgets:
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

  def window_resize(self, width, height) -> None:
    if self.fixed_size:
      self._width  = self.fixed_width  / width
      self._height = self.fixed_height / height

      if self.parent:
        self._width  /= self.parent.width
        self._height /= self.parent.height
        if not hasattr(self, '_position'):
          self._position = Vector3(self.fixed_position.x / (self.parent.width * width), self.fixed_position.y / (self.parent.height * height))

    self.propagate(Event.WINDOW_RESIZE, width, height)

  def click(self, *args) -> None:
    self.propagate(Event.CLICK, *args)

  def drag(self, *args) -> None:
    self.propagate(Event.DRAG, *args)

  def cursor(self, *args) -> None:
    self.propagate(Event.CURSOR, *args)

  def update(self, delta: float) -> None:
    self.propagate(Event.UPDATE, delta)

  def propagate(self, event, *args, **kwargs):
    fn_name = event.name.lower()
    for child in self.children.values():
      if (child.visible or event == Event.WINDOW_RESIZE) and hasattr(child, fn_name):
        fn = getattr(child, fn_name)
        fn(*args, **kwargs)

  def contains(self, point: Vector3) -> bool:
    """Return True if the point is inside the Widget."""
    inside_x = self.position.x <= point.x <= (self.position.x + self.width)
    inside_y = self.position.y <= point.y <= (self.position.y + self.height)

    return inside_x and inside_y