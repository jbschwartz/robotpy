import math

from robot.spatial           import euler
from robot.spatial.vector3   import Vector3
from robot.spatial.transform import Transform

# TODO: Candidate to be immutable to guarantee functions that receive Frame don't have side effects.
class Frame:
  def __init__(self, frame_to_world : Transform = None):
    self.frame_to_world = frame_to_world or Transform()

  @classmethod
  def from_position_orientation(cls, position: Vector3, orientation: 'Quaternion'):
    frame_to_world = Transform.from_orientation_translation(orientation, position)
    return cls(frame_to_world)

  def transform(self, transform):
    '''Return new transformed frame.'''
    return Frame(self.frame_to_world * transform)

  def position(self) -> Vector3:
    '''Frame origin.'''
    return self.frame_to_world.translation()

  def orientation(self):
    '''Frame orientation quaternion.'''
    return self.frame_to_world.rotation()

  def euler_angles(self, axes=None, order=None):
    '''
    Return frame orientation euler angles.

    Default to intrinsic ZYX.
    '''
    axes  = axes  or euler.Axes.ZYX
    order = order or euler.Order.INTRINSIC

    frame_orientation = self.frame_to_world.rotation()
    return euler.angles(frame_orientation, axes, order)

  def x(self):
    '''Frame x-axis vector.'''
    return self.frame_to_world(Vector3(1,0,0), as_type="vector")

  def y(self):
    '''Frame y-axis vector.'''
    return self.frame_to_world(Vector3(0,1,0), as_type="vector")

  def z(self):
    '''Frame z-axis vector.'''
    return self.frame_to_world(Vector3(0,0,1), as_type="vector")
