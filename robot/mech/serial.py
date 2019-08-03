import copy, itertools, math

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

    self.base.joint = Joint.Immovable()
    for link, joint in zip(self.links[1:], self.joints):
      link.joint = joint

    self.checkStructure()

    self.update_link_transforms()

  def checkStructure(self):
    # TODO: Check the structure of the robot to see if it is 6R with spherical wrist
    #   The code currently assumes this configuration only

    # Robots handled in this code _must_ have a shoulder that is perpendicular to the waist
    assert math.isclose(abs(self.links[1].joint.dh.alpha), math.pi / 2), 'Robot does not have a recognized shoulder configuration'

    # The elbow must be parallel to the shoulder joint (alpha dictates the angle between z-axes)
    correctElbow = math.isclose(self.links[2].joint.dh.alpha, 0) or math.isclose(self.links[2].joint.dh.alpha, math.pi)
    assert correctElbow, 'Robot does not have a recognized elbow configuration'

  @property
  def base(self) -> Link:
    """Return the robot's base Link."""
    return self.links[0]

  @property
  def robot_to_world(self) -> Transform:
    return self._robot_to_world

  @robot_to_world.setter
  def robot_to_world(self, transform) -> None:
    self._robot_to_world = transform
    self.base.update_transform(self.robot_to_world)

    self.update_link_transforms()

  @property
  def angles(self):
    return [link.joint.angle for link in self.links[1:]]

  @angles.setter
  def angles(self, angles):
    for angle, link in zip(angles, self.links[1:]):
      link.joint.angle = angle

    self.update_link_transforms()

  @property
  def aabb(self) -> AABB:
    return AABB(*[link.aabb for link in self.links])

  def attach(self, tool: Tool = None):
    '''Attach the tool to the robot's end effector.'''
    self.tool = tool

    self.update_link_transforms()

  def intersect(self, ray):
    if self.aabb.intersect(ray):
      return ray.closest_intersection(self.links)
    else:
      return None

  def update_link_transforms(self):
    last_link_transform = self.base.to_world
    # Walk the chain updating each link with it's previous neighbors transform
    for link in self.links[1:]:
      last_link_transform = link.update_transform(last_link_transform)

    # TODO: Move this into the loop above (by either adding tool to links list or concatenating on the spot)
    if self.tool is not None:
      self.tool.tool_to_world = self.links[-1].to_world

  def pose(self) -> Frame:
    if self.tool is not None:
      return Frame(self.tool.tip)
    else:
      return self.links[-1].frame

  def poses(self) -> list:
    return [link.frame for link in self.links]

  def upper_arm_length(self):
    return self.links[2].joint.dh.a

  def fore_arm_length(self):
    y = self.links[3].joint.dh.a
    x = self.links[4].joint.dh.d
    return math.sqrt(y ** 2 + x ** 2)

  def shoulder_wrist_offset(self):
    return self.links[2].joint.dh.d + self.links[3].joint.dh.d

  def shoulder_z(self):
    return self.links[1].joint.dh.d

  def within_limits(self, qs : list):
    return all(map(lambda joint, q: joint.within_limits(q), self.joints, qs))

  def transform_to_robot(self, angle_sets):
    '''
    Takes generic joint angles and transforms them to this specific robot's geometry
    '''

    zero = {
      'waist': self.links[1].joint.dh.theta,
      'shoulder': self.links[2].joint.dh.theta,
      'elbow': math.atan(self.links[4].joint.dh.d / self.links[3].joint.dh.a)
    }

    direction = {
      'shoulder': 1 if self.links[1].joint.dh.alpha > 0 else -1
    }
    direction['elbow'] = -direction['shoulder'] if self.links[2].joint.dh.alpha == math.pi else direction['shoulder']

    for angles in angle_sets:
      angles[0] -= zero['waist']
      angles[1] = direction['shoulder'] * angles[1] - zero['shoulder']
      angles[2] = direction['elbow'] * (angles[2] + zero['elbow'])

  def wrist_center(self, pose : Frame):
    '''Get wrist center point given the end-effector pose and tool.'''
    wrist_length = self.links[6].joint.dh.d

    tip_transform = Transform()
    if self.tool is not None:
      tip_transform = self.tool._tip.inverse()

    total = pose.frame_to_world * tip_transform * Transform.from_axis_angle_translation(translation=Vector3(0, 0, -wrist_length))

    return total.translation()