import enum, math

from .exceptions import *
from .facet import Facet
from .mesh import Mesh

from ..common import Timer
from ..spatial import Vector3

@enum.unique
class ParserState(enum.Enum):
  PARSE_SOLID = enum.auto()
  PARSE_FACET = enum.auto()
  PARSE_NORMAL = enum.auto()
  PARSE_LOOP = enum.auto()
  PARSE_VERTEX = enum.auto()

  def __str__(self):
    return self.name.replace('PARSE_', '').replace('_', ' ').lower()

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
        raise STLStateError(self.current['line'], self.current["state"], f.__name__)
    return wrapper
  return _check_state

class STLParser:
  KEYWORD_WHITELIST = ('solid', 'color', 'facet', 'normal', 'outer', 'vertex', 'endloop', 'endfacet', 'endsolid')

  def __init__(self, warnings = True):
    self.meshes = []
    self.warnings = dict()
    self.show_warnings = warnings

    self.reset()

  def reset(self):
    self.current = {
      'state': ParserState.PARSE_SOLID,
      'facet': Facet(),
      'line': 1
    }

    self.stats = {
      'facets': 0,
      'vertices': 0,
      'elapsed': 0
    }

  def parse(self, file):
    # Assuming ASCII format for now
    with Timer() as timer:
      # Reset all the state information in case we parse multiple times
      self.reset()

      for line in file:
        self.consume(line.strip())
        self.current['line'] += 1

    self.stats['elapsed'] = timer.elapsed

    return self.meshes

  def add_warning(self, warning_type : WarningType):
    # Store the line that generated the warning to display to the user
    if isinstance(warning_type, WarningType):
      self.warnings[warning_type] = self.current['line']

  def parse_components(self, keyword, components_string):
    try:
      components = list(map(float, components_string.split(' ')))
    except ValueError:
      raise STLFloatError(self.current['line'], keyword)

    if len(components) != 3:
      raise STLUnexpectedSize(self.current['line'], keyword)

    return components

  def consume(self, line):
    # Ignore case
    keyword, *rest = line.lower().split(' ', 1)

    if keyword in self.KEYWORD_WHITELIST:
      fn = getattr(self, keyword)
    else:
      raise ParserError(self.current['line'], f'Unknown keyword: {keyword}')

    # For these keywords, convert string to list of floats
    if keyword in ['color', 'normal', 'vertex']:
      rest = self.parse_components(keyword, *rest)
    
    fn(*rest)

  @check_state(ParserState.PARSE_SOLID)
  def solid(self, name):
    self.current['mesh'] = Mesh(name)
    self.current['state'] = ParserState.PARSE_FACET

  @check_state(ParserState.PARSE_FACET)
  def color(self, r, g, b):
    # Check that color components are floating point values between 0 and 1
    if self.show_warnings and not all(0.0 <= color_component <= 1 for color_component in [r, g, b]):
      self.add_warning(WarningType.INVALID_COLOR)

    self.current['mesh'].set_color(r, g, b)

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

    if self.show_warnings and not n.is_unit():
      self.add_warning(WarningType.NON_UNIT_NORMAL)
      n.normalize()

    self.current['facet'].passed_normal = n
    self.current['state'] = ParserState.PARSE_LOOP

  @check_state(ParserState.PARSE_LOOP)
  def outer(self, loop_keyword = None):
    if self.show_warnings and loop_keyword != 'loop':
      self.add_warning(WarningType.NO_LOOP_KEYWORD)

    self.current['state'] = ParserState.PARSE_VERTEX

  @check_state(ParserState.PARSE_VERTEX)
  def vertex(self, x, y, z):
    v = Vector3(x, y, z)
    self.current['facet'].vertices.append(v)
    self.stats['vertices'] += 1
  
  @check_state(ParserState.PARSE_VERTEX)
  def endloop(self):
    facet = self.current['facet'] 

    if not facet.is_triangle():
      raise STLNotATriangle(self.current['line'], facet.size())

    self.current['state'] = ParserState.PARSE_LOOP

  @check_state(ParserState.PARSE_LOOP)
  def endfacet(self):
    try:
      if self.show_warnings and self.current['facet'].has_conflicting_normal():
        self.add_warning(WarningType.CONFLICTING_NORMALS)
    except DegenerateTriangleError:
      self.add_warning(WarningType.DEGENERATE_TRIANGLE)

    self.current['mesh'].facets.append(self.current['facet'])
    self.current['state'] = ParserState.PARSE_FACET

  @check_state(ParserState.PARSE_FACET)
  def endsolid(self, name):
    if self.show_warnings:
      # We know we've seen at least one valid facet if the current facet is a triangle
      if not self.current['facet'].is_triangle():
        self.add_warning(WarningType.EMPTY_SOLID)

      # Make sure the name of the endsolid call matches the opening solid call
      if name != self.current['mesh'].name:
        self.add_warning(WarningType.END_SOLID_NAME_MISMATCH)
    
    self.meshes.append(self.current['mesh'])
    self.current['state'] = ParserState.PARSE_SOLID