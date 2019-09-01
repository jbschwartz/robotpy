import json, os

from robot.spatial import Mesh, Transform, Vector3
from robot.visual.filetypes.stl.stl_parser import STLParser

dir_path = os.path.dirname(os.path.realpath(__file__))

def load(file_path: str) -> 'Tool':
  with open(file_path) as json_file:
    data = json.load(json_file)

  mesh_transform = Transform.from_json(data['mesh']['transform'])

  stl_parser = STLParser()
  mesh, *_ = Mesh.from_file(stl_parser, f'{dir_path}/tools/meshes/{data["mesh"]["file"]}')

  mesh = mesh.scale(data["mesh"]["scale"])

  # Move the mesh onto a useful origin position if the modeler decided to include positional or rotational offsets
  mesh = mesh.transform(mesh_transform)

  tip_transform = Transform.from_json(data['tip_transform'])

  return Tool(tip_transform, mesh)

class Tool:
  """Attachable robot end effector."""
  def __init__(self, tip: Transform, mesh: 'Mesh') -> None:
    # Transformation of the tool origin to world space
    self.to_world = Transform.from_axis_angle_translation()
    self._tip = tip
    self.mesh = mesh

  @property
  def tip(self) -> Transform:
    """Returns the transform of the tool tip in world space."""
    return self.to_world * self._tip

  @property
  def offset(self) -> Vector3:
    """Return the offset of the tool tip to tool_base in world space."""
    return self._tip.translation()