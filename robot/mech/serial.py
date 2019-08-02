import copy, itertools, math

from robot                   import constant
from robot.mech.joint        import Joint
from robot.mech.link         import Link
from robot.mech.tool         import Tool
from robot.spatial.aabb      import AABB
from robot.spatial.frame     import Frame
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

class Serial:
  def __init__(self, joints : list, links = []):
    self._robot_to_world = Transform()
    self.joints = joints
    self.links = links
    self.traj = None
    self.qs = [0] * 6
    self.tool = None

    self.checkStructure()

    self.update_links()

  def checkStructure(self):
    print(self.joints[0].dh)
    # TODO: Check the structure of the robot to see if it is 6R with spherical wrist
    #   The code currently assumes this configuration only

    # Robots handled in this code _must_ have a shoulder that is perpendicular to the waist
    assert math.isclose(abs(self.joints[0].dh.alpha), math.pi / 2), 'Robot does not have a recognized shoulder configuration'

    # The elbow must be parallel to the shoulder joint (alpha dictates the angle between z-axes)
    correctElbow = math.isclose(self.joints[1].dh.alpha, 0) or math.isclose(self.joints[1].dh.alpha, math.pi)
    assert correctElbow, 'Robot does not have a recognized elbow configuration'

  @property
  def robot_to_world(self) -> Transform:
    return self._robot_to_world

  @robot_to_world.setter
  def robot_to_world(self, transform) -> None:
    self._robot_to_world = transform
    self.links[0].frame = self.links[0].frame.transform(self.robot_to_world)

    self.update_links()

  @property
  def angles(self):
    return [joint.angle for joint in self.joints]

  @angles.setter
  def angles(self, angles):
    for angle, joint in zip(angles, self.joints):
      joint.angle = angle

    self.update_links()

  @property
  def aabb(self) -> AABB:
    return AABB(*[link.aabb for link in self.links])

  def attach(self, tool: Tool = None):
    '''Attach the tool to the robot's end effector.'''
    self.tool = tool

    if self.tool:
      self.tool.tool_to_world = self.links[-1].frame.frame_to_world

  def intersect(self, ray):
    if self.aabb.intersect(ray):
      return ray.closest_intersection(self.links)
    else:
      return None

  def update_links(self):
    last_frame = self.links[0].frame
    for link, joint in zip(self.links[1:], self.joints):
      link.frame = last_frame.transform(joint.transform)
      last_frame = link.frame

    if self.tool is not None:
      self.tool.tool_to_world = self.links[-1].frame.frame_to_world

  def pose(self) -> Frame:
    if self.tool is not None:
      return Frame(self.tool.tip)
    else:
      return self.links[-1].frame

  def poses(self) -> list:
    return [link.frame for link in self.links]

  def upper_arm_length(self):
    return self.joints[1].dh.a

  def fore_arm_length(self):
    y = self.joints[2].dh.a
    x = self.joints[3].dh.d
    return math.sqrt(y ** 2 + x ** 2)

  def shoulder_wrist_offset(self):
    return self.joints[1].dh.d + self.joints[2].dh.d

  def shoulder_z(self):
    return self.joints[0].dh.d

  def within_limits(self, qs : list):
    return all(map(lambda joint, q: joint.within_limits(q), self.joints, qs))

  def transform_to_robot(self, angle_sets):
    '''
    Takes generic joint angles and transforms them to this specific robot's geometry
    '''

    zero = {
      'waist': self.joints[0].dh.theta,
      'shoulder': self.joints[1].dh.theta,
      'elbow': math.atan(self.joints[3].dh.d / self.joints[2].dh.a)
    }

    direction = {
      'shoulder': 1 if self.joints[0].dh.alpha > 0 else -1
    }
    direction['elbow'] = -direction['shoulder'] if self.joints[1].dh.alpha == math.pi else direction['shoulder']

    for angles in angle_sets:
      angles[0] -= zero['waist']
      angles[1] = direction['shoulder'] * angles[1] - zero['shoulder']
      angles[2] = direction['elbow'] * (angles[2] + zero['elbow'])

  def wrist_center(self, pose : Frame):
    '''Get wrist center point given the end-effector pose and tool.'''
    wrist_length = self.joints[5].dh.d

    tip_transform = Transform()
    if self.tool is not None:
      tip_transform = self.tool._tip.inverse()

    total = pose.frame_to_world * tip_transform * Transform.from_axis_angle_translation(translation=Vector3(0, 0, -wrist_length))

    return total.translation()