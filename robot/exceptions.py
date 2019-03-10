class RobotError(Exception):
  pass

class ParserError(RobotError):
  def __init__(self, msg, line):
    self.line = line
    super(ParserError, self).__init__(msg)