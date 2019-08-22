from numbers import Number
from typing  import Callable, Iterable, Union

from robot.utils import raise_if
from robot.spatial import Matrix4, Transform, Vector3

from .exceptions import UniformArraySizeError, UniformSizeError, UniformTypeError

def flatten_elements(element) -> Iterable[Number]:
  if isinstance(element, Vector3):
    return element.xyz
  elif isinstance(element, Transform):
    matrix = Matrix4.from_transform(element)
    return matrix.elements
  elif isinstance(element, Matrix4):
    return element.elements
  elif isinstance(element, (list, tuple)) and isinstance(element[0], Number):
    return element
  else:
    assert False, f"flatten_elements has not been implemented for {type(element)} but is listed as an accepetable_type to a decorator."

def flatten(iterable: Iterable, iterable_size: int, element_size: int, acceptable_types: Iterable) -> Iterable[Number]:
  if isinstance(iterable, acceptable_types) or (isinstance(iterable, (list, tuple)) and isinstance(iterable[0], Number)):
    iterable = [iterable]

  raise_if(
    len(iterable) != iterable_size,
    UniformArraySizeError(len(iterable), iterable_size, acceptable_types)
  )

  numbers = []
  for element in iterable:
    if not (isinstance(element, acceptable_types) or isinstance(element, (list, tuple))):
      raise UniformTypeError(type(element), acceptable_types)

    values = flatten_elements(element)

    raise_if(len(values) != element_size, UniformSizeError)
    numbers.extend(values)

  # This is an assertion since we should trigger an Uniform(Array)SizeError exception first
  assert len(numbers) == (iterable_size * element_size)
  assert all([isinstance(number, Number) for number in numbers])

  return numbers

def primative(gl_function: int, acceptable_type: type) -> Callable:
  def array_wrapper(array_size: int) -> Callable:
    def wrapper(location: int, values: Iterable) -> None:
      if isinstance(values, acceptable_type):
        values = [values]
      elif isinstance(values, (list, tuple)):
        for value in values:
          if not isinstance(value, acceptable_type):
            raise UniformTypeError(type(value), acceptable_type)
      else:
        raise UniformTypeError(type(values), acceptable_type)

      raise_if(
        len(values) != array_size,
        UniformArraySizeError(len(values), array_size, acceptable_type)
      )

      gl_function(location, array_size, values)
    return wrapper
  return array_wrapper

def vector(gl_function: int, vector_size: int) -> Callable:
  # TODO: Implement glUniform[1,2,4]xv functions
  assert vector_size == 3, "Only vectors of size 3 are implemented"

  acceptable_types = (Vector3,)

  def array_wrapper(array_size: int) -> Callable:
    def wrapper(location: int, values: Union[Vector3, Iterable]) -> None:
      numbers = flatten(values, array_size, vector_size, acceptable_types)
      gl_function(location, array_size, numbers)
    return wrapper
  return array_wrapper

def matrix(gl_function: int, matrix_size: int) -> Callable:
  # TODO: Implement non-square matricies
  # TODO: Implement glUniformMatrix[2,3]fv functions
  assert matrix_size == 4, "Only matricies of size 4 are implemented"

  acceptable_types = (Matrix4, Transform)

  def array_wrapper(array_size: int) -> Callable:
    def wrapper(location: int, values: Union[Iterable, Matrix4, Transform]) -> None:
      elements = flatten(values, array_size, matrix_size ** 2, acceptable_types)
      # Matrix4 stores elements column-major so transposing is never necessary for OpenGL
      gl_function(location, array_size, False, elements)
    return wrapper
  return array_wrapper
