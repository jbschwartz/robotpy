from typing import Iterable

from robot.exceptions import RobotError

class UniformArraySizeError(RobotError):
  def __init__(self, got_number: int, expected_number: int, expected_types: Iterable[type]):
    try:
      expected_type_string = ', '.join([f'`{expected.__name__}`' for expected in expected_types])
    except TypeError as e:
      expected_type_string = expected_types.__name__

    super().__init__(f'Expected {expected_number} {expected_type_string}(s), got {got_number} instead.')

class UniformSizeError(RobotError):
  pass

class UniformTypeError(RobotError):
  def __init__(self, got_type: type, expected_types: Iterable[type]):
    try:
      expected_type_string = ', '.join([f'`{expected.__name__}`' for expected in expected_types])
    except TypeError as e:
      expected_type_string = expected_types.__name__

    super().__init__(f'Unexpected Uniform value type `{got_type.__name__}` (expected {expected_type_string})')