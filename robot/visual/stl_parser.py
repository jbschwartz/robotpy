import enum, math, traceback

from .mesh import Mesh
from .facet import Facet

from ..spatial import vector3

Vector3 = vector3.Vector3

@enum.unique
class ParserState(enum.Enum):
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
  INVALID_COLOR = enum.auto()
  EMPTY_SOLID = enum.auto()
  END_SOLID_NAME_MISMATCH = enum.auto()

def check_state(expected_state):
  def _check_state(f):
    def wrapper(self, *args):
      if self.state is expected_state:
        return f(self, *args)
      else:
        state_name = self.state.name.replace('PARSE_', '').replace('_', ' ').lower()
        new_state = f.__name__.replace('begin_', '').replace('_', '').lower()
        raise Exception(f'While parsing {state_name} state, unexpected transition to {new_state} state on line {self.current_line}')
    return wrapper
  return _check_state

class STLParser:
  def __init__(self):
    self.meshes = []
    self.state = ParserState.PARSE_SOLID
    self.current_facet = Facet()
    self.warnings = dict()

  def parse(self, filename):
    # Assuming ASCII format for now
    with open(filename, 'r') as f:
      self.warnings.clear()
      self.current_line = 1

      for line in f:
        try:
          self.consume(line.strip())
          self.current_line += 1
        except Exception as error:
          print(traceback.format_exc())
          print(f'Parsing error: {error.args[0]}')
          return None
      
      self.print_warnings()

    return self.meshes

  def add_warning(self, warning_type : WarningType):
    # Store the line that generated the warning to display to the user
    self.warnings[warning_type] = self.current_line

  def print_warnings(self):
    for warning_type, line in self.warnings.items():
      message = 'Unknown warning'
      if warning_type is WarningType.NON_UNIT_NORMAL:
        message = 'Non-unit normal'
      elif warning_type is WarningType.CONFLICTING_NORMALS:
        message = 'Conflicting facet normal'
      elif warning_type is WarningType.INVALID_COLOR:
        message = 'Invalid color'
      elif warning_type is WarningType.EMPTY_SOLID:
        message = 'Empty solid'
      elif warning_type is WarningType.END_SOLID_NAME_MISMATCH:
        message = 'Wrong endsolid name'

      print(f'Warning: {message} provided on line {line}')

  def parse_components(self, components_string):
    return list(map(float, components_string.split(' ')))

  def consume(self, line):
    # Ignore case
    keyword, *rest = line.lower().split(' ', 1)
    if keyword == 'solid':
      self.begin_solid(rest[0])
    elif keyword == 'color':
      self.solid_color(*self.parse_components(rest[0]))
    elif keyword == 'facet':
      self.begin_facet()

      self.consume(rest[0])
    elif keyword == 'normal':
      try:
        self.normal(*self.parse_components(rest[0]))
      except TypeError:
        raise Exception('Normal contains an invalid number of components')
      except ValueError:
        raise Exception('Normal component cannot be converted to float')
    elif keyword == 'outer' and rest[0] == 'loop':
      self.begin_loop()
    elif keyword == 'vertex':
      try:
        self.vertex(*self.parse_components(rest[0]))
      except TypeError:
        raise Exception('Vertex contains an invalid number of components')
      except ValueError:
        raise Exception('Vertex component cannot be converted to float')
    elif keyword == 'endloop':
      self.end_loop()
    elif keyword == 'endfacet':
      self.end_facet()
    elif keyword == 'endsolid':
      self.end_solid(rest[0])
    else:
      raise Exception(f'Encountered unknown keyword: {keyword}')

  @check_state(ParserState.PARSE_SOLID)
  def begin_solid(self, name):
    self.meshes.append(Mesh(name))
    self.state = ParserState.PARSE_FACET

  @check_state(ParserState.PARSE_FACET)
  def solid_color(self, r, g, b):
    # Check that color components are floating point values between 0 and 1
    if not all(0.0 <= color_component <= 1 for color_component in [r, g, b]):
      self.add_warning(WarningType.INVALID_COLOR)

    self.meshes[-1].set_color(r, g, b)

  @check_state(ParserState.PARSE_FACET)
  def begin_facet(self):  
    self.current_facet = Facet()
    self.state = ParserState.PARSE_NORMAL

  @check_state(ParserState.PARSE_NORMAL)
  def normal(self, x, y, z):
    n = Vector3(x, y, z)

    if not n.is_unit():
      self.add_warning(WarningType.NON_UNIT_NORMAL)
      n.normalize()

    self.current_facet.passed_normal = n
    self.state = ParserState.PARSE_LOOP

  @check_state(ParserState.PARSE_LOOP)
  def begin_loop(self):
    self.state = ParserState.PARSE_VERTEX

  @check_state(ParserState.PARSE_VERTEX)
  def vertex(self, x, y, z):
    if self.current_facet.is_complete():
      raise Exception(f'Too many vertices given for facet')
    
    v = Vector3(x, y, z)
    self.current_facet.vertices.append(v)
  
  @check_state(ParserState.PARSE_VERTEX)
  def end_loop(self):
    if not self.current_facet.is_complete():
      raise Exception(f'Loop does not contain exactly 3 vertices')

    self.state = ParserState.PARSE_FACET_COMPLETE

  @check_state(ParserState.PARSE_FACET_COMPLETE)
  def end_facet(self):
    if self.current_facet.has_conflicting_normal():
      self.add_warning(WarningType.CONFLICTING_NORMALS)

    self.meshes[-1].add_facet(self.current_facet)
    self.state = ParserState.PARSE_FACET

  @check_state(ParserState.PARSE_FACET)
  def end_solid(self, name):    
    # We know we've seen at least one facet if the current facet is complete
    if not self.current_facet.is_complete():
      self.add_warning(WarningType.EMPTY_SOLID)

    # Make sure the name of the endsolid call matches the opening solid call
    if name != self.meshes[-1].name:
      self.add_warning(WarningType.END_SOLID_NAME_MISMATCH)
    
    self.state = ParserState.PARSE_SOLID