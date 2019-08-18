import numpy as np

from numbers import Number
from typing  import Callable, Iterable, Union

from robot.spatial import Matrix4, Transform, Vector3

def primative(gl_function: int) -> Callable:
  def array_wrapper(array_size: int) -> Callable:
    def wrapper(location: int, values: Iterable) -> None:
      if isinstance(values, Number):
        assert array_size == 1
        gl_function(location, 1, [values])
      else:
        assert len(values) == array_size
        gl_function(location, array_size, values)

    return wrapper
  return array_wrapper

def vector(gl_function: int, vector_size: int) -> Callable:
  def array_wrapper(array_size: int) -> Callable:
    # TODO: Implement glUniform[1,2,4]xv functions
    assert vector_size == 3, "Only vectors of size 3 are implemented"

    def wrapper(location: int, values: Union[Vector3, Iterable]) -> None:
      if array_size == 1:
        if isinstance(values, Vector3):
          return gl_function(location, 1, [*values])
        else:
          assert len(values) == vector_size, "Wrong vector size"
          return gl_function(location, 1, values)

      assert len(values) == array_size, f"Incorrect number of vectors passed. Got {len(values)}, expected {array_size}"
      assert isinstance(values, (list, tuple)), "Vector array must be passed a list or tuple"

      components = []
      for value in values:
        assert len(value) == vector_size, "Incorrect vector size"
        assert all([isinstance(component, Number) for component in value]), "All components must be numeric"

        # The type of value must support unpacking
        components.extend([*value])

      gl_function(location, len(values), components)

    return wrapper
  return array_wrapper

def matrix(gl_function) -> Callable:
  def array_wrapper(array_size: int) -> Callable:
    def wrapper(location, transforms):
      # TODO: Better type/size checking
      # This entire function is actually broken since there are glUniformMatrix[1,2,3,4]x functions
      # This assumes it's always 4
      if not isinstance(transforms, list):
        if isinstance(transforms, Transform):
          matrix = Matrix4.from_transform(transforms)
        elif isinstance(transforms, Matrix4):
          matrix = transforms

        return gl_function(location, 1, False, np.array(matrix.elements, dtype=np.float32))

      assert all(map(lambda m: isinstance(m, (Transform, Matrix4)), transforms))

      matrices = list(map(lambda t: Matrix4.from_transform(t) if isinstance(t, Transform) else t, transforms))

      # OpenGL expects a flat list of matrix elements
      elements = [elem for m in matrices for elem in m.elements]
      # Matrix4 stores elements column-major so transposing is never necessary for OpenGL
      return gl_function(location, len(matrices), False, elements)

    return wrapper
  return array_wrapper
