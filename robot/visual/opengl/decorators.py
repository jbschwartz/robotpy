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
  # TODO: Implement glUniform[1,2,4]xv functions
  assert vector_size == 3, "Only vectors of size 3 are implemented"

  def array_wrapper(array_size: int) -> Callable:
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

def matrix(gl_function: int, matrix_size: int) -> Callable:
  # TODO: Implement non-square matricies
  # TODO: Implement glUniformMatrix[2,3]fv functions
  assert matrix_size == 4, "Only matricies of size 4 are implemented"

  def array_wrapper(array_size: int) -> Callable:
    def wrapper(location: int, values: Union[Iterable, Matrix4, Transform]) -> None:
      # Handle `= Matrix4()`, `= Transform()`, Handle `= [1, 2, ..., 16]`
      if isinstance(values, (Matrix4, Transform)) or isinstance(values[0], Number):
        values = [values]

      assert isinstance(values, (list, tuple))
      assert len(values) == array_size, f"Incorrect number of matricies passed. Got {len(values)}, expected {array_size}"

      elements = []

      for value in values:
        if isinstance(value, Transform):
          matrix = Matrix4.from_transform(value)
          components = matrix.elements
        elif isinstance(value, Matrix4):
          components = value.elements
        elif isinstance(value[0], Number):
          components = value
        else:
          raise TypeError(f'Unexpected type {type(value)} given to Matrix Array')

        assert len(components) == 16
        elements.extend(components)

      # Matrix4 stores elements column-major so transposing is never necessary for OpenGL
      return gl_function(location, array_size, False, elements)

    return wrapper
  return array_wrapper
