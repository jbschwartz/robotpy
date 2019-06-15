import enum

# TODO: Rename this enum or split it into multiple enums
class WindowEvents(enum.Enum):
  START_RENDERER = enum.auto()
  START_FRAME    = enum.auto()
  UPDATE         = enum.auto()
  DRAW           = enum.auto()
  END_FRAME      = enum.auto()
  END_RENDERER   = enum.auto()
  WINDOW_RESIZE  = enum.auto()
  CURSOR         = enum.auto()
  ZOOM           = enum.auto()

  def __str__(self):
    return self.name.lower()