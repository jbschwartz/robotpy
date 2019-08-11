import math

from collections import namedtuple

from robot         import constant
from robot.spatial import Dual, Quaternion, Transform
from .exceptions   import InvalidJointAngleError, InvalidJointDictError

# TODO: Generalize this class to potentially handle prismatic case

DenavitHartenberg = namedtuple('DenavitHartenberg', 'alpha a theta d')

JointLimits = namedtuple('JointLimits', 'low high', defaults=(-math.inf, math.inf))

# TODO: Think about allowing the construction of a joint from a Transform instead of just
#   through DH parameters.

class Joint:
  def __init__(self, dh: DenavitHartenberg, limits: JointLimits = None) -> None:
    self.dh = dh

    self._angle = 0

    self.limits = limits or JointLimits()

    # Swap limits if they are out of order
    if limits.low > limits.high:
      self.limits = JointLimits(limits.high, limits.low)

  @classmethod
  def Immovable(cls) -> 'Joint':
    """Construct a Joint that does not move or transform its link.

    This is primarily useful for giving the base link of a robot a dummy joint transform.
    """
    return cls(DenavitHartenberg(0, 0, 0, 0), JointLimits(0, 0))

  @classmethod
  def from_dict(cls, d: dict) -> 'Joint':
    """Construct a Joint from a dictionary of parameters."""
    dh_dict = d.get('dh', None)

    if not dh_dict or not all(key in dh_dict for key in DenavitHartenberg._fields):
      raise InvalidJointDictError('Missing required Denavit-Hartenberg parameter for Joint construction')

    dh = DenavitHartenberg(
      math.radians(dh_dict['alpha']),
                   dh_dict['a'],
      math.radians(dh_dict['theta']),
                   dh_dict['d']
    )

    # Convert limits to radians (if they are provided)
    # Take only fields that exist in the JointLimits namedtuple
    limit_dictionary = {
      k: math.radians(v)
      for k, v in d.get('limits', {}).items()
      if k in JointLimits._fields
    }

    joint_limits = JointLimits(**limit_dictionary)

    return cls(dh, joint_limits)

  @property
  def angle(self) -> float:
    return self._angle

  @angle.setter
  def angle(self, value) -> None:
    if not self.within_limits(value):
      raise InvalidJointAngleError(f"{value} outside of joint limits [{self.limits.low}, {self.limits.high}]")

    self._angle = value

  @property
  def transform(self) -> Transform:
    return self.transform_at(self.angle)

  def transform_at(self, angle: float = None) -> Transform:
    """The joint's spatial DH transformation given an angle."""
    # This is derived and precomputed from the following sequence of transformations, applied left to right:
    #   Translate_z(d), Rotate_z(theta), Translate_x(a), Rotate_x(alpha)
    # See Joint tests for the geometrically and mathematically intuitive version

    theta = (self.dh.theta + angle) / 2

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

  @property
  def travel_in_revs(self) -> int:
    """The integer number of revolutions the joint is capable of traveling."""
    return int(self.travel // (2 * math.pi))

  def within_limits(self, q) -> bool:
    """Return True if the provided angle is within joint limits. False otherwise."""
    if q == constant.SINGULAR:
      return True

    return self.limits.low <= q <= self.limits.high
