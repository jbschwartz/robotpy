import glfw, math

from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class SerialController():
  def __init__(self, serial: Serial) -> None:
    self.serial = serial

  def joint_controller_factory(self, joint_index: int) -> Callable[[str, float], None]:
    def callback(name: str, value: float) -> None:
      self.serial.set_joint_angle(joint_index, value, normalized=True)
    return callback
