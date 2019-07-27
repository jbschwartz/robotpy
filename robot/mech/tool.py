from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

class Tool:
  '''Attachable robot end effector.'''
  def __init__(self, tip: 'Transform', mesh: 'Mesh') -> None:
    # Transformation of the tool origin to world space
    self.tool_to_world = Transform()
    self.tip = tip
    self.mesh = mesh

  @property
  def translation(self) -> 'Vector3':
    '''Return the location of the tool tip in the tool frame.'''
    return self.tip.translation()