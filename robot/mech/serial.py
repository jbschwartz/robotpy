import copy, itertools, json, math

from .joint import Joint
from .link import Link

from ..spatial import Dual, Quaternion, Transform, Frame, Vector3
from robot import constant

def load(filename):
  joints = []
  links = []
  with open(filename) as json_file:  
    data = json.load(json_file)

    for joint_params in data['joints']:
      for param, value in joint_params.items():
        if param == 'limits':
          value['low'] = math.radians(value['low'])
          value['high'] = math.radians(value['high'])
        elif param in ['alpha', 'theta']:
          joint_params[param] = math.radians(value)

      joints.append(Joint(**joint_params))

    for link_parameters in data['links']:
      link_parameters['mesh_file'] = data['mesh_file']
      links.append(Link(**link_parameters))

  return Serial(joints, links)

class Serial:
  def __init__(self, joints : list, links = []):
    self.joints = joints
    self.links = links
    self.position = Vector3()

    self.qs = [0] * 6

    self.checkStructure()

  def checkStructure(self):
    # TODO: Check the structure of the robot to see if it is 6R with spherical wrist
    #   The code currently assumes this configuration only

    # Robots handled in this code _must_ have a shoulder that is perpendicular to the waist
    assert math.isclose(abs(self.joints[0].dh['alpha']), math.pi / 2), 'Robot does not have a recognized shoulder configuration'
    
    # The elbow must be parallel to the shoulder joint (alpha dictates the angle between z-axes)
    correctElbow = math.isclose(self.joints[1].dh['alpha'], 0) or math.isclose(self.joints[1].dh['alpha'], math.pi)
    assert correctElbow, 'Robot does not have a recognized elbow configuration'

  def pose(self) -> Frame: 
    t = Transform()

    for joint, value in itertools.zip_longest(self.joints, self.qs, fillvalue=0):
      t *= joint.transform(value)

    return Frame(t)

  def current_transforms(self) -> list: 
    ts = [ Transform() ]
    
    for joint, value in itertools.zip_longest(self.joints, self.qs, fillvalue=0):
      # Get last frame
      t = copy.deepcopy(ts[-1])
      t *= joint.transform(value)
      ts.append(t)
    
    return ts

  def poses(self) -> list: 
    ts = self.current_transforms()

    return [ Frame(t) for t in ts ]

  def upper_arm_length(self):
    return self.joints[1].dh['a']

  def fore_arm_length(self):
    y = self.joints[2].dh['a']
    x = self.joints[3].dh['d']
    return math.sqrt(y ** 2 + x ** 2)

  def shoulder_wrist_offset(self):
    return self.joints[1].dh['d'] + self.joints[2].dh['d']

  def shoulder_z(self):
    return self.joints[0].dh['d']

  def within_limits(self, qs : list):
    for q, joint in zip(qs, self.joints):
      if q != constant.SINGULAR:
        if q < joint.limits['low'] or q > joint.limits['high']:
          return False
    return True

  def transform_to_robot(self, angle_sets):
    '''
    Takes generic joint angles and transforms them to this specific robot's geometry
    '''

    zero = {
      'waist': self.joints[0].dh['theta'],
      'shoulder': self.joints[1].dh['theta'],
      'elbow': math.atan(self.joints[3].dh['d'] / self.joints[2].dh['a'])
    }

    direction = {
      'shoulder': 1 if self.joints[0].dh['alpha'] > 0 else -1
    }
    direction['elbow'] = -direction['shoulder'] if self.joints[1].dh['alpha'] == math.pi else direction['shoulder']

    for angles in angle_sets:
      angles[0] -= zero['waist']
      angles[1] = direction['shoulder'] * angles[1] - zero['shoulder']
      angles[2] = direction['elbow'] * (angles[2] + zero['elbow'])

  def wrist_center(self, pose : Frame):
    '''
    Get wrist center point given the end-effector pose
    '''
    # TODO: Handle tools
    wrist_length = self.joints[5].dh['d']
    return pose.position() - pose.z() * wrist_length
