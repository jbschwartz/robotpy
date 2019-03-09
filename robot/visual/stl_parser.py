import enum, math

from .mesh import Mesh
from .facet import Facet

from ..spatial import vector3

Vector3 = vector3.Vector3

@enum.unique
class ParserState(enum.Enum):
  READY = enum.auto()
  PARSE_SOLID = enum.auto()
  PARSE_FACET = enum.auto()
  PARSE_NORMAL = enum.auto()
  PARSE_LOOP = enum.auto()
  PARSE_VERTEX = enum.auto()
  PARSE_FACET_COMPLETE = enum.auto()

@enum.unique
class WarningType(enum.Enum):
  NON_UNIT_NORMAL = enum.auto()
  CONFLICTING_NORMALS = enum.auto()

# TODO: How to keep warning state?
# warnings = {
#   NON_UNIT_NORMAL: {
#     'message':
#     'line':
#   }
# }

# TODO: How to pass current state into error messages?
def state_name(state):
  pass

class STLParser:
  def __init__(self):
    self.meshes = []
    self.state = ParserState.READY
    self.current_facet = Facet()
    self.warnings = set()

  def parse(self, filename):
    # Assuming ASCII format for now
    with open(filename, 'r') as f:
      self.warnings.clear()
      self.current_line = 0

      for line in f:
        try:
          self.consume(line.strip())
          # TODO: Use this variable in exception messages. Thanks @atomfighter.
          self.current_line += 1
        except Exception as error:
          print(f'Parsing error: {error.args[0]}')
          return None
      
      for warning_type in self.warnings:
        message = ''
        print(f'Warning: {message}')

    return self.meshes

  def parse_components(self, components_string):
    return list(map(float, components_string.split(' ')))

  def consume(self, line):
    # Ignore case
    keyword, rest = line.lower().split(' ', 1)
    if keyword == 'solid':
      self.begin_solid(rest)
    elif keyword == 'color':
      # TODO: Check that the color make senses; for example: float values between 0 and 1
      self.solid_color(*self.parse_components(rest))
    elif keyword == 'facet':
      self.begin_facet()

      consume(rest)
    elif keyword == 'normal':
      try:
        self.normal(*self.parse_components(rest))
      except TypeError:
        raise Exception('Normal contains an invalid number of components')
      except ValueError:
        raise Exception('Normal component cannot be converted to float')
    elif keyword == 'outer' and rest == 'loop':
      self.begin_loop()
    elif keyword == 'vertex':
      try:
        self.vertex(*self.parse_components(rest))
      except TypeError:
        raise Exception('Vertex contains an invalid number of components')
      except ValueError:
        raise Exception('Vertex component cannot be converted to float')
    elif keyword == 'endloop':
      self.end_loop()
    elif keyword == 'endfacet':
      self.end_facet()
    elif keyword == 'endsolid':
      self.end_solid(rest)
    else:
      raise Exception(f'Encountered unknown keyword: {keyword}')

  def begin_solid(self, name):
    if self.state is ParserState.READY:
      self.meshes.append(Mesh(name))
      self.state = ParserState.PARSE_SOLID
    else:
      raise Exception('Unexpected solid')

  def solid_color(self, r, g, b):
    # TODO: Check if STL allows per facet or per vertex coloring
    # If so, we need to allow more states here
    if self.state is ParserState.PARSE_SOLID:
      self.meshes[-1].set_color(r, g, b)
    else:
      raise Exception('Unexpected color')

  def begin_facet(self):
    if self.state is ParserState.PARSE_SOLID:
      self.current_facet = Facet()
      self.state = ParserState.PARSE_NORMAL
    else:
      raise Exception('Unexpected facet')

  def normal(self, x, y, z):
    # TODO: Check if STL allows this to be optional
    if self.state is ParserState.PARSE_NORMAL:
      n = Vector3(x, y, z)

      # TODO: Replace with Vector3.is_unit()
      if not math.isclose(n.length, 1.0):
        self.warnings.add(WarningType.NON_UNIT_NORMAL)
        n.normalize()

      self.current_facet.passed_normal = n
      self.state = ParserState.PARSE_LOOP
    else:
      raise Exception('Unexpected normal')

  def begin_loop(self):
    if self.state is ParserState.PARSE_FACET:
      self.state = ParserState.PARSE_VERTEX
    else:
      raise Exception('Unexpected loop')

  def vertex(self, x, y, z):
    if self.state is ParserState.PARSE_VERTEX:
      if self.current_facet.is_complete():
        raise Exception(f'Too many vertices given for facet')
      
      v = Vector3(x, y, z)
      self.current_facet.vertices.append(v)
    else:
      raise Exception('Unexpected vertex')
  
  def end_loop(self):
    if self.state is ParserState.PARSE_VERTEX:
      if self.current_facet.is_complete():
        raise Exception(f'Loop does not contain exactly 3 vertices')

      self.state = ParserState.PARSE_FACET_COMPLETE
    else:
      raise Exception(f'Cannot close loop in {state_name(self.state)}')

  def end_facet(self):
    if self.state is ParserState.PARSE_FACET_COMPLETE:
      if self.current_facet.has_conflicting_normal():
        self.warnings.add(WarningType.CONFLICTING_NORMALS)

      self.meshes[-1].add_facet(self.current_facet)
      self.state = ParserState.PARSE_SOLID
    else:
      raise Exception(f'Cannot close facet in {state_name(self.state)}')

  def end_solid(self, rest):
    if self.state is ParserState.PARSE_SOLID:
      # We know we've seen at least one facet if the current facet is complete
      if not self.current_facet.is_complete():
        # TODO: Should this be a warning instead?
        raise Exception(f'Solid is empty')

      # TODO: Make sure the name of the endsolid call matches the opening solid call
      # Make this a warning
    else:
      raise Exception(f'Cannot close solid in {state_name(self.state)}')