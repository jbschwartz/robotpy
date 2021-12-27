import abc, math

from spatial import Transform, vector3

class Segment(abc.ABC):
  @abc.abstractmethod
  def interpolate(self, t: float) -> 'Vector3':
    pass

  @abc.abstractmethod
  def reverse(self) -> None:
    pass

class LinearSegment(Segment):
  '''A linear point-to-point segment.'''
  def __init__(self, start: 'Vector3', end: 'Vector3'):
    self.start = start
    self.end   = end

    assert not math.isclose(self.length, 0), 'Zero length LinearSegment.'

  def __str__(self) -> str:
    return f"{self.start} -> {self.end} (Linear)"

  @property
  def direction(self) -> 'Vector3':
    '''Return the normalized direction vector of the segment.'''
    return vector3.normalize(self.end - self.start)

  @property
  def length(self) -> float:
    '''Return the length of the segment.'''
    return (self.end - self.start).length()

  def interpolate(self, t: float) -> 'Vector3':
    '''Return point on the segment for the given parameter t in [0, 1].'''
    assert 0 <= t <= 1, 'Parameter `t` outside domain [0, 1]'
    return (self.end - self.start) * t + self.start

  def reverse(self) -> None:
    '''Change the direction of the segment.'''
    self.start, self.end = self.end, self.start


class ArcSegment(Segment):
  '''A three-point arc segment.'''
  def __init__(self, start: 'Vector3', end: 'Vector3', center: 'Vector3'):
    self.start  = start
    self.end    = end
    self.center = center

    assert math.isclose(self.start_edge.length(), self.end_edge.length()), 'ArcSegment `start` and `end` have different radii.'
    assert not math.isclose(self.start_edge * self.end_edge, 1), 'Ambiguous ArcSegment: `start` and `end` are parallel.'
    assert not math.isclose(self.radius, 0), 'ArcSegment with zero radius.'

  @classmethod
  def create_blend(cls, first: LinearSegment, second: LinearSegment, radius: float) -> 'ArcSegment':
    '''Create an ArcSegment by blending two LinearSegments.'''
    assert first.end == second.start

    half_angle_between = vector3.angle_between(-first.direction, second.direction) / 2

    try:
      distance = radius / math.tan(half_angle_between)
    except ZeroDivisionError:
      # We have an issue if the segments are colinear. They're not blendable
      return None

    if distance > first.length or distance > second.length:
      # No blend (radius clobbers the segment(s))
      return None

    p = first.end + distance * -first.direction
    q = first.end + distance * second.direction

    normal = first.direction % second.direction

    direction_to_center = (normal % first.direction).normalize()

    center = p + radius * direction_to_center

    return cls(p, q, center)

  def __str__(self) -> str:
    return f"{self.start} -> {self.end} (center: {self.center})"

  @property
  def start_edge(self) -> 'Vector3':
    return self.start - self.center

  @property
  def end_edge(self) -> 'Vector3':
    return self.end - self.center

  @property
  def radius(self) -> float:
    '''Return the radius of the circular sector.'''
    return self.start_edge.length()

  @property
  def central_angle(self) -> float:
    '''Return the central angle of the circular sector.'''
    return vector3.angle_between(self.start_edge, self.end_edge)

  @property
  def length(self) -> float:
    '''Return the circular sector arc length.'''
    return self.radius * self.central_angle

  @property
  def axis(self) -> 'Vector3':
    '''Return the axis (normal) of the circular sector.'''
    return (self.start_edge % self.end_edge).normalize()


  def interpolate(self, t: float) -> 'Vector3':
    '''Return point on the segment for the given parameter t in [0, 1].'''
    assert 0 <= t <= 1, 'Parameter `t` outside domain [0, 1]'
    theta = self.central_angle * t
    transform = Transform.from_axis_angle_translation(self.axis, theta)

    return self.center + transform(self.start_edge)

  def reverse(self) -> None:
    '''Change the direction of the segment.'''
    self.start, self.end = self.end, self.start
