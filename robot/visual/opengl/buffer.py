import numpy as np

from copy   import deepcopy
from ctypes import c_void_p
from typing import Iterable

from robot.common    import logger
from spatial         import Mesh, Vector3
from .shader_program import ShaderProgram

from OpenGL.GL import *

MESH_BUFFER_ATTRS = {
  'position':   {'type': GL_FLOAT, 'number_of_components': 3},
  'normal':     {'type': GL_FLOAT, 'number_of_components': 3},
  'mesh_index': {'type': GL_INT,   'number_of_components': 1},
}

ATTRIBI_TYPES = (GL_BYTE, GL_UNSIGNED_BYTE, GL_SHORT, GL_UNSIGNED_SHORT, GL_INT, GL_UNSIGNED_INT)

def get_buffer_data(mesh: Mesh, index: int = 0) -> np.array:
    """Return a numpy array of flattened, interleaved vertex position and normal floats.
    Index is useful for storing multiple meshes in a single OpenGL buffer.
    This allows the shader program to distinguish between meshes.
    """
    data = [
      ([*vertex, *(facet.normal)], index)
      for facet in mesh.facets
      for vertex in facet.vertices
    ]

    return np.array(data, dtype=[('', np.float32, 6),('', np.int32)])


class Buffer():
  """OpenGL Buffer instance."""
  def __init__(self, data: np.array = None, attributes: dict = None, size: int = None) -> None:
    self.vao = glGenVertexArrays(1)

    if data is not None:
      if len(data) == 0 or attributes is None:
        return logger.warn(f"Buffer given no data or no vertex attributes to access it.")
      elif size is not None:
        logger.warn(f"Buffer size passed but ignored (since data is provided).")

      self.vbo        = glGenBuffers(1)
      self.data       = data
      self.attributes = attributes
    else:
      if size is None:
        return logger.warn(f"Buffer given no data, attributes, or size.")

      self._size = size

  def __len__(self) -> int:
    """Return the number of elements in the buffer."""
    if self.is_procedural:
      return self._size
    else:
      return len(self.data)

  def __enter__(self) -> 'Buffer':
    glBindVertexArray(self.vao)
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
    glBindVertexArray(0)

  @classmethod
  def from_mesh(cls, mesh: Mesh) -> 'Buffer':
    """Create a Buffer from a Mesh."""
    data = np.array(get_buffer_data(mesh), dtype=[('', np.float32, 6),('', np.int32)])
    # TODO: Maybe there is something better than a deepcopy
    return cls(data, deepcopy(MESH_BUFFER_ATTRS))

  @classmethod
  def from_meshes(cls, meshes: Iterable[Mesh]) -> 'Buffer':
    """Create one Buffer for a collection of Meshes."""
    data = np.array([], dtype=[('', np.float32, 6),('', np.int32)])
    for mesh_index, mesh in enumerate(meshes):
      mesh_data = get_buffer_data(mesh, mesh_index)
      data = np.concatenate((data, mesh_data), axis=0)

    # TODO: Maybe there is something better than a deepcopy
    return cls(data, deepcopy(MESH_BUFFER_ATTRS))

  @classmethod
  def from_points(cls, points: Iterable[Vector3]) -> 'Buffer':
    """Create one Buffer for a collection of Vector3 points."""
    data_list = [(point.xyz,) for point in points]
    data = np.array(data_list, dtype=[('', np.float32, 3)])

    return cls(data, {
      'position': {'type': GL_FLOAT, 'number_of_components': 3}
    })

  @classmethod
  def Procedural(cls, size) -> 'Buffer':
    """Create an empty buffer for 'procedural' shader programs."""
    return cls(None, None, size)

  @property
  def is_procedural(self) -> bool:
    return not (hasattr(self, 'data') and hasattr(self, 'attributes'))

  @property
  def stride(self) -> int:
    # np.itemsize gets the size of one element (read: vertex) in the data array
    return self.data.itemsize

  def set_attribute_locations(self, sp: ShaderProgram) -> None:
    if self.is_procedural:
      return

    for attribute_name in self.attributes.keys():
      try:
        self.attributes[attribute_name]['location'] = sp.attribute_location(f'vin_{attribute_name}')
      except AttributeError:
        logger.warn(f'Attribute `vin_{attribute_name}` not found in shader program `{sp.name}`')

  def load(self) -> None:
    if self.is_procedural:
      return

    assert any(
      [
        'location' in parameters
        for parameters in self.attributes.values()
      ]
    ), "Buffer attribute locations must be set before the buffer can be loaded"

    glBindVertexArray(self.vao)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, self.data.nbytes, self.data, GL_STATIC_DRAW)

    offset = 0
    for parameters in self.attributes.values():
      if parameters.get('location', None) is None:
        continue

      if parameters['type'] in ATTRIBI_TYPES:
        glVertexAttribIPointer(
          parameters['location'],
          parameters['number_of_components'],
          parameters['type'],
          self.stride,
          c_void_p(offset)
        )
      else:
        glVertexAttribPointer(
          parameters['location'],
          parameters['number_of_components'],
          parameters['type'],
          GL_FALSE,
          self.stride,
          c_void_p(offset)
        )

      # TODO: Do not assume that all buffer values are four bytes
      offset += 4 * parameters['number_of_components']

      glEnableVertexAttribArray(parameters['location'])

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
