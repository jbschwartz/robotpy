import abc

from typing import Iterable

from robot.traj.segment import ArcSegment, LinearSegment

class Path(abc.ABC):
  @abc.abstractmethod
  def length(self) -> float:
    pass

class PiecewisePath(Path):
  '''A path consisting of a collection of Segment primitives.'''
  def __init__(self, segments: Iterable['Segment']) -> None:
    self.segments = segments

  @classmethod
  def from_waypoints(cls, waypoints: Iterable['Vector3']) -> 'PiecewisePath':
    '''Return a PiecewisePath from a list of waypoints.'''
    return cls([
      LinearSegment(start, end)
      for start, end
      in zip(waypoints[0:-1], waypoints[1:])
    ])

  def __str__(self) -> str:
    segment_strs = [f"{index}: {segment}" for index, segment in enumerate(self.segments, 1)]
    return '\n'.join(segment_strs)

  @property
  def is_closed(self) -> bool:
    '''Return whether or not the path is closed.'''
    return self.segments[0].start == self.segments[-1].end

  @property
  def length(self) -> float:
    '''Return the length of the PiecewisePath.'''
    return sum([segment.length for segment in self.segments])

  @property
  def number_of_segments(self) -> int:
    '''Return the number of segments in the PiecewisePath.'''
    return len(self.segments)

  def blend(self, radius: float) -> None:
    '''Blend all linear segments in the PiecewisePath with `radius`.'''
    new_segments = []
    last_endpoint = self.segments[0].start

    for first, second in zip(self.segments[0:-1], self.segments[1:]):
      # Segment direction vectors
      blend = ArcSegment.create_blend(first, second, radius)

      if blend is not None:
        new_first_segment = LinearSegment(last_endpoint, blend.start)

        last_endpoint = blend.end

        new_segments.extend([
            new_first_segment,
            blend
        ])
      else:
        new_first_segment = LinearSegment(first.start, first.end)
        new_segments.append(new_first_segment)
        last_endpoint = first.end

    new_segments.append(LinearSegment(last_endpoint, second.end))

    if self.is_closed:
      blend = ArcSegment.create_blend(self.segments[-1], self.segments[0], radius)

      if blend is not None:
        new_segments[0].start = blend.end
        new_segments[-1].end = blend.start

        new_segments.append(blend)

    self.segments = new_segments

  def reverse(self) -> None:
    '''Reverse the direction of the path.'''
    self.segments.reverse()

    for segment in self.segments:
      segment.reverse()

