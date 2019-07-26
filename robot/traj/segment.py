import abc, math

from robot.spatial           import vector3
from robot.spatial.transform import Transform

class Segment(abc.ABC):
  @abc.abstractmethod
  def interpolate(self, t: float) -> 'Vector3':
    pass

class LinearSegment(Segment):
  def __init__(self, start: 'Vector3', end: 'Vector3'):
    self.start = start
    self.end   = end

    assert not math.isclose(self.length, 0), 'Zero length LinearSegment.'

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


class ArcSegment(Segment):
  def __init__(self, start: 'Vector3', end: 'Vector3', center: 'Vector3'):
    self.start  = start - center
    self.end    = end - center
    self.center = center

    assert math.isclose(self.start.length(), self.end.length()), 'ArcSegment `start` and `end` have different radii.'
    assert not math.isclose(self.start * self.end, 1), 'Ambiguous ArcSegment: `start` and `end` are parallel.'
    assert not math.isclose(self.radius, 0), 'ArcSegment with zero radius.'

  @property
  def radius(self) -> float:
    '''Return the radius of the circular sector.'''
    return self.start.length()

  @property
  def central_angle(self) -> float:
    '''Return the central angle of the circular sector.'''
    return vector3.angle_between(self.start, self.end)

  @property
  def length(self) -> float:
    '''Return the circular sector arc length.'''
    return self.radius * self.central_angle

  @property
  def axis(self) -> 'Vector3':
    '''Return the axis (normal) of the circular sector.'''
    return (self.start % self.end).normalize()


  def interpolate(self, t: float) -> 'Vector3':
    '''Return point on the segment for the given parameter t in [0, 1].'''
    assert 0 <= t <= 1, 'Parameter `t` outside domain [0, 1]'
    theta = self.central_angle * t
    transform = Transform.from_axis_angle_translation(self.axis, theta)

    return self.center + transform(self.start)