import math

from collections import namedtuple

from robot.spatial.dual       import Dual
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform
from robot.spatial.vector3    import Vector3

# TODO: Generalize this class to potentially handle prismatic case

DenavitHartenberg = namedtuple('DenavitHartenberg', 'alpha, a, theta, d')

class Joint:
  def __init__(self, dh: DenavitHartenberg, limits):
    self.dh = dh

    self.angle = 0

    self.limits = {}
    if all(key in limits for key in ('low', 'high')):
      if limits['low'] > limits['high']:
        limits['low'], limits['high'] = limits['high'], limits['low']
      self.limits['low'] = limits['low']
      self.limits['high'] = limits['high']
    else:
      raise KeyError()

    # Precompute quaternions for the joint transform
    self.alpha = Quaternion.from_axis_angle(Vector3(1, 0, 0), self.dh.alpha)
    self.a = Quaternion(0, self.dh.a, 0, 0)
    self.a_alpha = self.a * self.alpha
    self.d = Quaternion(0, 0, 0, self.dh.d)

  @classmethod
  def from_json(cls, json: dict) -> 'Joint':
    """Construct a joint from json dictionary."""
    try:
      dh = DenavitHartenberg(
        math.radians(json['dh']['alpha']),
                     json['dh']['a'],
        math.radians(json['dh']['theta']),
                     json['dh']['d']
      )
    except TypeError:
      raise KeyError('Missing required Denavit-Hartenberg parameter')

    # Set an unlimited joint by default if limits are not specified
    joint_limits = {
      **{
        'low': -math.inf,
        'high': math.inf
      },
      **{k: math.radians(v) for k, v in json['limits'].items()}
    }

    return cls(dh, joint_limits)

  @property
  def transform(self):
    '''
    Create transformation from Denavit-Hartenberg parameters

    Transform = Translate_z(d) * Rotate_z(theta) * Translate_x(a) * Rotate_x(alpha)
    '''

    angle_sum = self.dh.theta + self.angle
    theta = Quaternion.from_axis_angle(Vector3(0, 0, 1), angle_sum)
    r = theta * self.alpha
    dual = Dual(r, 0.5 * (theta * self.a_alpha + self.d * r))

    return Transform(dual)

  def num_revolutions(self):
    return math.floor((self.limits['high'] - self.limits['low']) / (2 * math.pi))
