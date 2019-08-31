import enum

class Event(enum.Enum):
  START_RENDERER = enum.auto()
  START_FRAME    = enum.auto()
  DRAW           = enum.auto()
  WINDOW_RESIZE  = enum.auto()
  CURSOR         = enum.auto()
  DRAG           = enum.auto()
  SCROLL         = enum.auto()
  CLICK          = enum.auto()
  KEY            = enum.auto()

  def __str__(self):
    return self.name.lower()