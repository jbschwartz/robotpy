from .dual       import Dual
from .transform  import Transform
from .quaternion import conjugate, Quaternion

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
      self.elements.extend([transformed_basis.x, transformed_basis.y, transformed_basis.z, 0])

    translation = 2 * d.d * r_star
    self.elements.extend([translation.x, translation.y, translation.z, 1])

  def __str__(self):
    def is_negative(string):
      return string[0] == '-'

    element_strings = list(map(str, self.elements))
    element_columns = [element_strings[i::4] for i in range(4)]
  
    has_negative = [False] * 4
    longest_elems = [0] * 4

    # Preprocess each column to see if a negative exists and what the longest element is
    for index, column in enumerate(element_columns):
      for element in column:
        if not has_negative[index] and is_negative(element):
          has_negative[index] = True
        
        if len(element) > longest_elems[index]:
          longest_elems[index] = len(element)

    lines = []
    for row_tuple in zip(*element_columns):
      row = []

      # In each row, look at each column
      for elem, col_is_negative, longest_elem in zip(row_tuple, has_negative, longest_elems):
        # Pad in front of the float if there is a negative in the column
        if col_is_negative and not is_negative(elem):
          elem = ' ' + elem
        
        # Pad behind the float if there is a longer element above or below
        elem += ' ' * (longest_elem - len(elem))

        row.append(elem)

      # Construct each line
      lines.append(", ".join(row))

    for index, line in enumerate(lines[1:], 1):
      lines[index] = '  ' + line

    separator = '\n'

    return f'[ {separator.join(lines)} ]'