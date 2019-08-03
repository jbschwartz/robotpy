import math

from collections import namedtuple

from robot                    import constant
from robot.spatial.dual       import Dual
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform

# TODO: Generalize this class to potentially handle prismatic case

DenavitHartenberg = namedtuple('DenavitHartenberg', 'alpha a theta d')

JointLimits = namedtuple('JointLimits', 'low high', defaults=(-math.inf, math.inf))

class Joint:
  def __init__(self, dh: DenavitHartenberg, limits: JointLimits) -> None:
    self.dh = dh

    self.angle = 0

    self.limits = limits

    # Swap limits if they are out of order
    if limits.low > limits.high:
      self.limits = JointLimits(limits.high, limits.low)

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

    # Convert limits to radians
    limit_dictionary = {k: math.radians(v) for k, v in json['limits'].items()}

    # Set an unlimited joint by default if limits are not specified
    joint_limits = JointLimits(
      limit_dictionary.get('low', None),
      limit_dictionary.get('high', None)
    )

    return cls(dh, joint_limits)

  @property
  def transform(self) -> Transform:
    """The joint's transformation given its angle."""
    # This is derived and precomputed from the following sequence of transformations, applied left to right:
    #   Translate_z(d), Rotate_z(theta), Translate_x(a), Rotate_x(alpha)
    # See Joint tests for the geometrically and mathematically intuitive version

    theta = (self.dh.theta + self.angle) / 2

    ct = math.cos(theta)
    st = math.sin(theta)

    ca = math.cos(self.dh.alpha / 2)
    sa = math.sin(self.dh.alpha / 2)

    ctca = ct * ca
    ctsa = ct * sa
    stca = st * ca
    stsa = st * sa

    return Transform(
      Dual(
        Quaternion(
          ctca,
          ctsa,
          stsa,
          stca
        ),
        0.5 * Quaternion(
          -self.dh.a * ctsa - self.dh.d * stca,
           self.dh.a * ctca - self.dh.d * stsa,
           self.dh.a * stca + self.dh.d * ctsa,
          -self.dh.a * stsa + self.dh.d * ctca
        )
      )
    )

  @property
  def travel(self) -> float:
    """The amount of travel the joint is capable of."""
    return self.limits.high - self.limits.low

  def num_revolutions(self) -> int:
    return int(self.travel // (2 * math.pi))

  def within_limits(self, q) -> bool:
    """Return True if the provided angle is within joint limits. False otherwise."""
    if q == constant.SINGULAR:
      return True

    return self.limits.low <= q <= self.limits.high
