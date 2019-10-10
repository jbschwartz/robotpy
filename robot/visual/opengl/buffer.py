import numpy     as np
import OpenGL.GL as gl

from collections import namedtuple
from ctypes      import c_void_p
from typing      import Iterable

from robot.common    import logger
from robot.spatial   import Mesh, Vector3
from .shader_program import ShaderProgram
from .               import constants

Attribute = namedtuple('Attribute', 'location, num_components, type, offset')

class Buffer():
  """OpenGL Buffer instance."""
  def __init__(self, data: np.array, is_procedural: bool = False) -> None:
    if len(data) == 0:
      raise AttributeError("Buffer has no data.")

    self.attributes    = []
    self.data          = data
    self.is_procedural = is_procedural
    self.vao           = gl.glGenVertexArrays(1)

    if not self.is_procedural:
      self.vbo = gl.glGenBuffers(1)

  def __len__(self) -> int:
    """Return the number of elements in the buffer."""
    return len(self.data)

  def __enter__(self) -> 'Buffer':
    gl.glBindVertexArray(self.vao)
    return self

  def __exit__(self, *args) -> None:
    gl.glBindVertexArray(0)

  @classmethod
  def from_mesh(cls, mesh: Mesh) -> 'Buffer':
    """Create a Buffer from a Mesh."""
    data = np.array(
      mesh.get_buffer_data(),
      dtype=[('position', '3f4'), ('normal', '3f4'), ('mesh_index', 'i4')]
    )

    return cls(data)

  @classmethod
  def from_meshes(cls, meshes: Iterable[Mesh]) -> 'Buffer':
    """Create one Buffer for a collection of Meshes."""
    mesh_data = []
    for mesh_index, mesh in enumerate(meshes):
      mesh_data.extend(mesh.get_buffer_data(mesh_index))

    data = np.array(
      mesh_data,
      dtype=[('position', '3f4'), ('normal', '3f4'), ('mesh_index', 'i4')]
    )

    return cls(data)

  @classmethod
  def from_points(cls, points: Iterable[Vector3]) -> 'Buffer':
    """Create one Buffer for a collection of Vector3 points."""
    data_list = [(point.xyz,) for point in points]

    return cls(np.array(data_list, dtype=[('position', '3f4')]))

  @classmethod
  def from_points_textured(cls, points: Iterable[float]) -> 'Buffer':
    """Create one Buffer for a collection of Vector3 points."""
    data = np.array(points, dtype=[('position', '3f4'), ('texCoords', '2f4')])

    return cls(data)

  @classmethod
  def Procedural(cls, size) -> 'Buffer':
    """Create an empty buffer for 'procedural' shader programs."""
    return cls(np.empty(size), True)

  @property
  def stride(self) -> int:
    # np.itemsize gets the size of one element (read: vertex) in the data array
    return self.data.itemsize

  def locate_attributes(self, sp: ShaderProgram) -> None:
    """Locate attributes from the given Shader Program."""
    if self.is_procedural:
      return
    # Get necessary vertex attribute information from the numpy data type
    for name, (attribute_type, offset) in self.data.dtype.fields.items():
      try:
        location = sp.attribute_location(f'vin_{name}')
      except AttributeError:
        logger.warn(f'Attribute `vin_{name}` not found in shader program `{sp.name}`')
        continue

      gl_type = constants.TYPE_NUMPY_TO_GL[attribute_type.base]
      num_components = 1 if not attribute_type.shape else attribute_type.shape[0]

      self.attributes.append(
        Attribute(location, num_components, gl_type, c_void_p(offset))
      )

  def reload(self, data_list) -> None:
    self.data = np.array(data_list, dtype=[('', np.float32, 5)])

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data.nbytes, self.data, gl.GL_STREAM_DRAW)

  def load(self) -> None:
    """Load the OpenGL buffer with the data and enable the attributes."""
    if self.is_procedural:
      return

    gl.glBindVertexArray(self.vao)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data.nbytes, self.data, gl.GL_STATIC_DRAW)

    for location, num_components, gl_type, offset in self.attributes:
      if gl_type in constants.GL_INTEGER_TYPES:
        gl.glVertexAttribIPointer(location, num_components, gl_type, self.stride, offset)
      elif gl_type in constants.GL_FLOAT_TYPES:
        gl.glVertexAttribPointer(location, num_components, gl_type, gl.GL_FALSE, self.stride, offset)

      gl.glEnableVertexAttribArray(location)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)