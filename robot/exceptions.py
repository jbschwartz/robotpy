class RobotError(Exception):
  def __init__(self, message = None):
    super().__init__(message)

class ParserError(RobotError):
  def __init__(self, msg, line):
    self.line = line
    super(ParserError, self).__init__(msg)