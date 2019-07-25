import math

from robot.ik.angles          import solve_angles
from robot.spatial.frame      import Frame
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform
from robot.spatial.dual       import Dual
from robot.spatial            import vector3
from robot.traj.segment       import Segment, SegmentType
from robot.traj.trajectory_js import TrajectoryJS
from robot.traj.utils         import interpolate

Vector3 = vector3.Vector3

def calculate_blend(first, second, radius) -> (Vector3, Vector3):
  half_angle_between = vector3.angle_between(-first.direction, second.direction) / 2

  try:
    distance = radius / math.tan(half_angle_between)
  except ZeroDivisionError:
    # We have an issue if the segments are colinear. They're not blendable
    return None, None

  if distance > first.length or distance > second.length:
    # No blend (radius clobbers the segment(s))
    return None, None

  p = first.end + distance * -first.direction
  q = first.end + distance * second.direction

  normal = first.direction % second.direction

  direction_to_center = (normal % first.direction).normalize()

  center = p + radius * direction_to_center

  return p, q, center

def calculate_blends(segments, radius = 0.375):
  new_segments = []
  last_endpoint = segments[0].start

  for first, second in zip(segments[0:-1], segments[1:]):
    # Segment direction vectors
    blend_start, blend_end, center = calculate_blend(first, second, radius)

    if blend_start:
      new_first_segment = Segment(last_endpoint, blend_start, SegmentType.LINEAR)
      new_blend_segment = Segment(blend_start, blend_end, SegmentType.ARC)
      new_blend_segment.center = center
      last_endpoint = blend_end

      new_segments.extend([
          new_first_segment,
          new_blend_segment
      ])
    else:
      new_first_segment = Segment(first.start, first.end, SegmentType.LINEAR)
      new_segments.append(new_first_segment)
      last_endpoint = first.end

  new_segments.append(Segment(last_endpoint, second.end, SegmentType.LINEAR))

  if segments[0].start == segments[-1].end:
    blend_start, blend_end, center = calculate_blend(segments[-1], segments[0], radius)

    if blend_start:
      new_segments[0].start = blend_end
      new_segments[-1].end = blend_start
      new_blend_segment = Segment(blend_start, blend_end, SegmentType.ARC)
      new_blend_segment.center = center
      new_segments.append(new_blend_segment)

  return new_segments

def interpolate_blend(start: Vector3, end: Vector3, center: Vector3, t: float) -> Vector3:
  radius_start = (start - center)
  radius_end = (end - center)

  angle_between = vector3.angle_between(radius_start, radius_end)
  # print(math.degrees(angle_between))


  normal = (radius_start % radius_end).normalize()

  radius = radius_start.length()

  assert radius > 0

  angle = angle_between * t

  transform = Transform.from_axis_angle_translation(normal, angle)

  return center + transform(radius_start)

def print_segments(segments):
  print('Segments: ')
  for index, segment in enumerate(segments, 1):
    print(f"{index}: {segment}")


class LinearOS():
  '''Linear trajectory in operational space.'''
  def __init__(self, robot, waypoints, duration = 1):
    self.segments = [
      Segment(start, end)
      for start, end
      in zip(waypoints[0:-1], waypoints[1:])
    ]

    self.segments = calculate_blends(self.segments, radius = 45)


    print_segments(self.segments)

    self.overall_length = sum([segment.length for segment in self.segments])

    self.segment_duration = [segment.length / self.overall_length * duration for segment in self.segments]

    self._segment_index = 0

    self._is_done = False

    self._t = 0
    self.direction = 1

    self.robot = robot
    self.robot.angles = [0] * 6

  @property
  def t(self):
    return self._t

  @t.setter
  def t(self, value):
    self._t = value

  @property
  def segment_index(self):
    return self._segment_index

  @segment_index.setter
  def segment_index(self, value):
    self._segment_index += 1
    if self._segment_index == self.number_of_segments:
      self._is_done = True
      self._segment_index = 0

  @property
  def number_of_segments(self):
    return len(self.segments)

  def calculate_new_target(self):
    segment = self.segments[self.segment_index]

    if segment.path_type == SegmentType.LINEAR:
      world_position = interpolate(segment.start, segment.end, self.t)
    else:
      world_position = interpolate_blend(segment.start, segment.end, segment.center, self.t)

    return Frame.from_position_orientation(world_position, self.robot.pose().orientation())

  def is_done(self):
    return self._is_done

  def restart(self):
    self._is_done = False
    self.t = 0

  def reverse(self):
    self.segments.reverse()
    self.segments = [(segment[1], segment[0]) for segment in self.segments]

  def get_closest_solution(self, solutions):
    '''Return the closest solution (in joint space) to the current arm position.'''
    current = self.robot.angles

    least    = math.inf
    solution = None

    for angles in solutions:
      joint_space_distance = sum([(new - current) ** 2
                                  for new, current in zip(angles, current)])

      if joint_space_distance < least:
        least    = joint_space_distance
        solution = angles

    return solution

  def advance(self, delta):
    assert delta >= 0

    if self._is_done:
      return self.robot.angles

    self.t += self.direction * (delta / self.segment_duration[self.segment_index])

    if self.t > 1:
      self.t -= 1
      self.segment_index += 1

    target = self.calculate_new_target()

    solutions = solve_angles(target, self.robot)

    return self.get_closest_solution(solutions)