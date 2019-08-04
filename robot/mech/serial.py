import itertools, math

from typing import Iterable

from robot.mech.exceptions import InvalidSerialDictError
from robot.mech.joint      import Joint
from robot.mech.link       import Link
from robot.mech.tool       import Tool
from robot.spatial         import AABB, Frame, Transform, Vector3
from robot.visual.mesh     import Mesh

class Serial:
  def __init__(self, links):
    self.links = links
    self.tool = None

    self.checkStructure()

    self.update_link_transforms()

  @classmethod
  def from_dict_meshes(cls, d: dict, meshes: Iterable[Mesh]) -> 'Serial':
    """Construct a Serial robot from provided dictionary and meshes.

    If there are more Links than Meshes, the Link is provided an empty Mesh."""
    link_dictionary = d.get('links', None)
    if not link_dictionary or not isinstance(link_dictionary, (list, tuple)):
      raise InvalidSerialDictError

    return cls(
      [
        Link.from_dict_mesh(link, mesh)
        for link, mesh
        in itertools.zip_longest(link_dictionary, meshes, fillvalue=Mesh())
      ]
    )

  def checkStructure(self):
    # TODO: Check the structure of the robot to see if it is 6R with spherical wrist
    #   The code currently assumes this configuration only

    # Robots handled in this code _must_ have a shoulder that is perpendicular to the waist
    assert math.isclose(abs(self.links[1].joint.dh.alpha), math.pi / 2), 'Robot does not have a recognized shoulder configuration'

    # The elbow must be parallel to the shoulder joint (alpha dictates the angle between z-axes)
    correctElbow = math.isclose(self.links[2].joint.dh.alpha, 0) or math.isclose(self.links[2].joint.dh.alpha, math.pi)
    assert correctElbow, 'Robot does not have a recognized elbow configuration'

  # Temporary (probably) property
  @property
  def joints(self) -> Iterable[Joint]:
    """Return a list of robot Joint objects."""
    return [link.joint for link in self.links[1:]]

  @property
  def base(self) -> Link:
    """Return the robot's base Link."""
    return self.links[0]

  @property
  def to_world(self) -> Transform:
    return self.base.to_world

  @to_world.setter
  def to_world(self, transform) -> None:
    self.base.previous = transform

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
    # Walk the chain updating each link with it's previous neighbors transform
    for previous, link in zip(self.links[0:], self.links[1:]):
      link.previous = previous.to_world

    # TODO: Move this into the loop above (by either adding tool to links list or concatenating on the spot)
    if self.tool is not None:
      self.tool.tool_to_world = self.links[-1].to_world

  def pose(self) -> Frame:
    if self.tool is not None:
      return Frame(self.tool.tip)
    else:
      return self.links[-1].frame

  def pose_at(self, angles: Iterable[float]) -> Frame:
    t = self.base.to_world
    for link, angle in zip(self.links[1:], angles):
      t *= link.joint.transform_at(angle)

    if self.tool is not None:
      t *= self.tool._tip

    return Frame(t)

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
    joints = [link.joint for link in self.links[1:]]
    return all(map(lambda joint, q: joint.within_limits(q), joints, qs))

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