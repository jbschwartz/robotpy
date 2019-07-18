from robot.spatial.dual       import Dual
from robot.spatial.quaternion import conjugate, Quaternion
from robot.spatial.transform  import Transform

class Matrix4:
  def __init__(self, construct_from = None):
    '''
    4x4 Matrix in _column-major_ order.

    That is: contiguous elements in the list form columns (e.g. self.elements[0:4] is the first column of the matrix)
    '''
    self.elements = [0.0] * 16
    for diag_index in [0, 5, 10, 15]:
      self.elements[diag_index]  = 1.0

    if isinstance(construct_from, Dual):
      self.construct_from_dual(construct_from)
    elif isinstance(construct_from, Transform):
      self.construct_from_dual(construct_from.dual)
    elif isinstance(construct_from, list) and len(construct_from) == 16:
      self.elements = construct_from

  def construct_from_dual(self, d : Dual):
    self.elements = []

    r_star = conjugate(d.r)
    for basis in [(0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]:
      transformed_basis = d.r * Quaternion(*basis) * r_star
      self.elements.extend([*transformed_basis.xyz, 0])

    translation = 2 * d.d * r_star
    self.elements.extend([*translation.xyz, 1])

  def __str__(self):
    # Get the width of "widest" floating point number
    longest = max(map(len, map('{:.4f}'.format, self.elements)))
    # Pad the left of each element to the widest number found
    padded = list(map(lambda elem: f'{elem:>{longest}.4f}', self.elements))

    # Since the values are stored column-major, we need to "transpose"
    columns = [ padded[i:i+4] for i in range(0, 15, 4) ]

    # Join columns by commas and rows by new lines
    return '\n'.join(map(', '.join, zip(*columns)))