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

  def __str__(self):
    return self.name.replace('PARSE_', '').replace('_', ' ')

@enum.unique
class WarningType(enum.Enum):
  NON_UNIT_NORMAL = 'Non-unit normal'
  CONFLICTING_NORMALS = 'Conflicting facet normal'
  INVALID_COLOR = 'Invalid color'
  EMPTY_SOLID = 'Empty solid'
  END_SOLID_NAME_MISMATCH = 'Wrong endsolid name'
  NO_LOOP_KEYWORD = 'No loop keyword'
  DEGENERATE_TRIANGLE = 'Degenerate triangle'

def check_state(expected_state):
  def _check_state(f):
    def wrapper(self, *args):
      if self.current['state'] is expected_state:
        return f(self, *args)
      else:
        raise Exception(f'unexpected `{f.__name__}` while parsing `{self.current["state"]}`')
    return wrapper
  return _check_state

class STLParser:
  KEYWORD_WHITELIST = ('solid', 'color', 'facet', 'normal', 'outer', 'vertex', 'endloop', 'endfacet', 'endsolid')

  def __init__(self):
    self.meshes = []
    self.warnings = dict()
    
    self.current = {
      'state': ParserState.PARSE_SOLID,
      'facet': Facet(),
      'line': 1
    }

    self.stats = {
      'facets': 0,
      'vertices': 0
    }

  def parse(self, filename):
    # Assuming ASCII format for now
    with open(filename, 'r') as f:
      # Reset all the state information in case we parse multiple times
      self.__init__()

      for line in f:
        try:
          self.consume(line.strip())
          self.current['line'] += 1
        except Exception as error:
          print(traceback.format_exc())
          print('\033[91m' + f'Parsing error on line {self.current["line"]}: {error.args[0]}' + '\033[0m')
          return None
      
      self.print_stats()
      self.print_warnings()

    return self.meshes

  def add_warning(self, warning_type : WarningType):
    # Store the line that generated the warning to display to the user
    if isinstance(warning_type, WarningType):
      self.warnings[warning_type] = self.current['line']

  def print_warnings(self):
    for warning, line in self.warnings.items():
      # TODO: Clean up color codes
      print('\033[93m' + f'Warning: {warning.value} provided on line {line}' + '\033[0m')
  
  def print_stats(self):
    for key, number in self.stats.items():
      print(f'{key.capitalize()}: {number}')

  def parse_components(self, keyword, components_string):
    try:
      return list(map(float, components_string.split(' ')))
    except TypeError:
      raise Exception(f'{keyword.capitalize()} contains an invalid number of components')
    except ValueError:
      raise Exception(f'{keyword.capitalize()} component cannot be converted to float')

  def consume(self, line):
    # Ignore case
    keyword, *rest = line.lower().split(' ', 1)

    if keyword in self.KEYWORD_WHITELIST:
      fn = getattr(self, keyword)
    else:
      raise Exception(f'Encountered unknown keyword: {keyword}')

    # For these keywords, convert string to list of floats
    if keyword in ['color', 'normal', 'vertex']:
      rest = self.parse_components(keyword, *rest)
    
    fn(*rest)

  @check_state(ParserState.PARSE_SOLID)
  def solid(self, name):
    self.meshes.append(Mesh(name))
    self.current['state'] = ParserState.PARSE_FACET

  @check_state(ParserState.PARSE_FACET)
  def color(self, r, g, b):
    # Check that color components are floating point values between 0 and 1
    if not all(0.0 <= color_component <= 1 for color_component in [r, g, b]):
      self.add_warning(WarningType.INVALID_COLOR)

    self.meshes[-1].set_color(r, g, b)

  @check_state(ParserState.PARSE_FACET)
  def facet(self, normal):  
    self.current['facet'] = Facet()
    self.stats['facets'] += 1

    # Continue processing the normal
    self.current['state'] = ParserState.PARSE_NORMAL
    self.consume(normal)

  @check_state(ParserState.PARSE_NORMAL)
  def normal(self, x, y, z):
    n = Vector3(x, y, z)

    if not n.is_unit():
      self.add_warning(WarningType.NON_UNIT_NORMAL)
      n.normalize()

    self.current['facet'].passed_normal = n
    self.current['state'] = ParserState.PARSE_LOOP

  @check_state(ParserState.PARSE_LOOP)
  def outer(self, loop_keyword = None):
    if loop_keyword != 'loop':
      self.add_warning(WarningType.NO_LOOP_KEYWORD)

    self.current['state'] = ParserState.PARSE_VERTEX

  @check_state(ParserState.PARSE_VERTEX)
  def vertex(self, x, y, z):
    if self.current['facet'].is_complete():
      raise Exception(f'Too many vertices given for facet')
    
    v = Vector3(x, y, z)
    self.current['facet'].vertices.append(v)
    self.stats['vertices'] += 1
  
  @check_state(ParserState.PARSE_VERTEX)
  def endloop(self):
    if not self.current['facet'].is_complete():
      raise Exception(f'Loop does not contain exactly 3 vertices')

    self.current['state'] = ParserState.PARSE_LOOP

  @check_state(ParserState.PARSE_LOOP)
  def endfacet(self):
    try:
      if self.current['facet'].has_conflicting_normal():
        self.add_warning(WarningType.CONFLICTING_NORMALS)
      self.meshes[-1].facets.append(self.current['facet'])
    except:
      self.add_warning(WarningType.DEGENERATE_TRIANGLE)

    self.current['state'] = ParserState.PARSE_FACET

  @check_state(ParserState.PARSE_FACET)
  def endsolid(self, name):    
    # We know we've seen at least one facet if the current facet is complete
    if not self.current['facet'].is_complete():
      self.add_warning(WarningType.EMPTY_SOLID)

    # Make sure the name of the endsolid call matches the opening solid call
    if name != self.meshes[-1].name:
      self.add_warning(WarningType.END_SOLID_NAME_MISMATCH)
    
    self.current['state'] = ParserState.PARSE_SOLID