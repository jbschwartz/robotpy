from .dual      import Dual
from .transform import Transform

class Matrix4:
  def __init__(self, arg):
    self.elements = [0.0] * 16
    if isinstance(arg, Dual):
      self.construct_from_dual(arg)
    elif isinstance(arg, Transform):
      self.construct_from_dual(arg.dual)
  
  def construct_from_dual(self, d : Dual):
    drx2 = d.r.x ** 2
    dry2 = d.r.y ** 2
    drz2 = d.r.z ** 2

    drxy = d.r.x * d.r.y
    drxz = d.r.x * d.r.z
    dryz = d.r.y * d.r.z
    drxr = d.r.x * d.r.r
    dryr = d.r.y * d.r.r
    drzr = d.r.z * d.r.r

    self.elements[0]  = 1.0 - 2.0 * (dry2 + drz2)
    self.elements[1]  = 2.0 * (drxy + drzr)
    self.elements[2]  = 2.0 * (drxz - dryr)
    self.elements[3]  = 0.0
    self.elements[4]  = 2.0 * (drxy - drzr)
    self.elements[5]  = 1.0 - 2.0 * (drx2 + drz2)
    self.elements[6]  = 2.0 * (dryz + drxr)
    self.elements[7]  = 0.0
    self.elements[8]  = 2.0 * (drxz + dryr)
    self.elements[9]  = 2.0 * (dryz - drxr)
    self.elements[10] = 1.0 - 2.0 * (drx2 + dry2)
    self.elements[11] = 0.0
    self.elements[12] = 2.0 * (-d.d.r * d.r.x + d.d.x * d.r.r - d.d.y * d.r.z + d.d.z * d.r.y)
    self.elements[13] = 2.0 * (-d.d.r * d.r.y + d.d.x * d.r.z + d.d.y * d.r.r - d.d.z * d.r.x)
    self.elements[14] = 2.0 * (-d.d.r * d.r.z - d.d.x * d.r.y + d.d.y * d.r.x + d.d.z * d.r.r)
    self.elements[15] = 1.0

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