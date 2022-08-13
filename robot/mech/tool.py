import json, math, os

from spatial import AABB, Intersection, Mesh, Quaternion, Ray, Transform, Vector3
from spatial.euler import Axes, Order
from robot.visual.filetypes.stl.stl_parser import STLParser

dir_path = os.path.dirname(os.path.realpath(__file__))

def from_json(payload) -> 'Transform':
  try:
    axes  = Axes[payload['euler']['axes'].upper()]
    order = Order[payload['euler']['order'].upper()]
    angles_radians = list(map(math.radians, payload['euler']['angles']))
    orientation = Quaternion.from_euler(angles_radians, axes, order)

    translation = Vector3(*payload['translation'])

    return Transform.from_orientation_translation(orientation, translation)
  except KeyError:
    # TODO: This is a catchall. Will not provide very useful debugging or handling information
    #   This could be caused by the json file not having those particular keys present. Need to provide defaults
    # TODO: Handle unknown euler angle axes or order
    #   Maybe we can choose a default instead of just erroring out.
    raise

def load(file_path: str) -> 'Tool':
  with open(file_path) as json_file:
    data = json.load(json_file)

  mesh_transform = from_json(data['mesh']['transform'])

  stl_parser = STLParser()
  mesh, *_ = Mesh.from_file(stl_parser, f'{dir_path}/tools/meshes/{data["mesh"]["file"]}')

  mesh = mesh.scale(data["mesh"]["scale"])

  # Move the mesh onto a useful origin position if the modeler decided to include positional or rotational offsets
  mesh = mesh.transform(mesh_transform)

  tip_transform = from_json(data['tip_transform'])

  return Tool(data['name'], tip_transform, mesh)

class Tool:
  """Attachable robot end effector."""
  def __init__(self, name: str, tip: Transform, mesh: 'Mesh') -> None:
    self.name = name
    # Transformation of the tool origin to world space
    self.to_world = Transform.from_axis_angle_translation()
    self._tip = tip
    self.mesh = mesh

  @property
  def aabb(self) -> AABB:
    """Return the Tool's Mesh AABB in world space."""
    return AABB([self.to_world(corner) for corner in self.mesh.aabb.corners])

  @property
  def tip(self) -> Transform:
    """Returns the transform of the tool tip in world space."""
    return self.to_world * self._tip

  @property
  def offset(self) -> Vector3:
    """Return the offset of the tool tip to tool_base in world space."""
    return self._tip.translation

  def intersect(self, world_ray: Ray) -> Intersection:
    """Intersect a ray with Tool and return closest found Intersection. Return Intersection.Miss() for no intersection."""
    if not self.aabb.intersect(world_ray):
      return Intersection.Miss()

    world_to_tool = self.to_world.inverse()

    facet = self.mesh.intersect(world_ray.transform(world_to_tool))
    if facet.hit:
      # If we hit a facet, repackage the Intersection to report the Link being intersected
      return Intersection(facet.t, self)
    else:
      return facet
