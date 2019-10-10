import glfw

from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event
from .rectangle                      import Rectangle

@listener
class Character(Rectangle):
  def __init__(self, **options):
    super().__init__(**options)
    self.data = []
    self.char = 32


  # @listen(Event.KEY)
  # def new_char(self, key, action, modifiers):
  #   if action != glfw.PRESS:
  #     return

  #   if 65 <= key <= 90:
  #     if (modifiers & glfw.MOD_SHIFT) == 0:
  #       key += 32

  #   f = Font(32, 16, [])
  #   u, v = f.uv(chr(key))
  #   width = 0.0625

  #   self.data = [
  #     ([1,  0,  0,  u+width,  v+width],), # Top Right
  #     ([0,  0,  0,  u,  v+width],), # Top Left
  #     ([0,  1,  0,  u,  v],), # Bottom Left
  #     ([0,  1,  0,  u,  v],), # Bottom Left
  #     ([1,  1,  0,  u+width,  v],), # Bottom Right
  #     ([1,  0,  0,  u+width,  v+width],), # Top Right
  #   ]

  #   self.char += 1

  #   if self.char >= 64:
  #     self.char = 32
