from typing import Iterable

from .dual       import Dual
from .quaternion import conjugate, Quaternion
from .transform  import Transform

class Matrix4:
  def __init__(self, elements: Iterable[float] = None) -> None:
    """4x4 Matrix in _column-major_ order.

    That is: contiguous elements in the list form columns (e.g. self.elements[0:4] is the first column of the matrix)
    """
    if elements:
      if len(elements) != 16:
        raise TypeError('Matrix4 requires 16 floating point elements')

      self.elements = elements
    else:
      self.elements = [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
      ]

  @classmethod
  def from_transform(cls, transform: Transform) -> 'Matrix4':
    """Construct a Matrix4 from a Transform."""
    return cls.from_dual(transform.dual)

  @classmethod
  def from_dual(cls, dual : Dual) -> 'Matrix4':
    """Construct a Matrix4 from a Dual Quaternion."""
    elements = []

    r_star = conjugate(dual.r)
    for basis in [(0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]:
      transformed_basis = dual.r * Quaternion(*basis) * r_star
      elements.extend([*transformed_basis.xyz, 0])

    translation = 2 * dual.d * r_star
    elements.extend([*translation.xyz, 1])

    assert len(elements) == 16

    return cls(elements)

  def __str__(self) -> str:
    # Get the width of "widest" floating point number
    longest = max(map(len, map('{:.4f}'.format, self.elements)))
    # Pad the left of each element to the widest number found
    padded = list(map(lambda elem: f'{elem:>{longest}.4f}', self.elements))

    # Since the values are stored column-major, we need to "transpose"
    columns = [ padded[i:i+4] for i in range(0, 15, 4) ]

    # Join columns by commas and rows by new lines
    return '\n'.join(map(', '.join, zip(*columns)))