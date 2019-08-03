from robot.exceptions import RobotError

class InvalidJointAngleError(RobotError):
  def __init__(self, msg):
    super().__init__(msg)

class InvalidJointDictError(RobotError):
  def __init__(self, msg):
    super().__init__(msg)

class InvalidSerialDictError(RobotError):
  def __init__(self, msg):
    super().__init__(msg)