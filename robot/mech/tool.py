from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

class Tool:
  """Attachable robot end effector."""
  def __init__(self, tip: Transform, mesh: 'Mesh') -> None:
    # Transformation of the tool origin to world space
    self.tool_to_world = Transform.from_axis_angle_translation()
    self._tip = tip
    self.mesh = mesh

  @property
  def tip(self) -> Transform:
    """Returns the transform of the tool tip in world space."""
    return self.tool_to_world * self._tip

  @property
  def offset(self) -> Vector3:
    """Return the offset of the tool tip to tool_base in world space."""
    return self._tip.translation()