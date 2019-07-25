import enum, math

from robot.spatial import vector3

class SegmentType(enum.Enum):
  LINEAR = enum.auto()
  ARC    = enum.auto()

class Segment():
  def __init__(self, start: 'Vector3', end: 'Vector3', path_type: SegmentType = SegmentType.LINEAR):
    self.start     = start
    self.end       = end
    self.path_type = path_type

  def __str__(self):
    return f"{self.start} -> {self.end} ({self.path_type}) (Length: {self.length})"

  @property
  def direction(self) -> 'Vector3':
    return vector3.normalize(self.end - self.start)

  @property
  def length(self) -> float:
    if self.path_type == SegmentType.ARC:
      radius = (self.start - self.center).length()
      print(radius)
      radius_start = (self.start - self.center)
      radius_end = (self.end - self.center)
      theta = vector3.angle_between(radius_start, radius_end)
      print(math.degrees(theta))
      return radius * theta
    else:
      return (self.end - self.start).length()