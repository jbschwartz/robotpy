import glfw

class Bindings():
  def __init__(self):
    # TODO: We can eventually save and load this from disk for user settings
    # TODO: Does glfw guarantee there is no overlap on their constants? (e.g. can MOUSE_BUTTON_MIDDLE be confused with a KEY_?)
    # Always place modifers before keys/buttons
    self.bindings = {
      (0,                glfw.MOUSE_BUTTON_MIDDLE): 'orbit',
      (glfw.MOD_CONTROL, glfw.MOUSE_BUTTON_MIDDLE): 'track',
      (glfw.MOD_ALT,     glfw.MOUSE_BUTTON_MIDDLE): 'roll',
      (glfw.MOD_SHIFT,   glfw.MOUSE_BUTTON_MIDDLE): 'scale',

      (0, glfw.KEY_LEFT):  'orbit_left',
      (0, glfw.KEY_RIGHT): 'orbit_right',
      (0, glfw.KEY_UP):    'orbit_up',
      (0, glfw.KEY_DOWN):  'orbit_down',

      (glfw.MOD_CONTROL, glfw.KEY_LEFT):  'track_right',
      (glfw.MOD_CONTROL, glfw.KEY_RIGHT): 'track_left',
      (glfw.MOD_CONTROL, glfw.KEY_UP):    'track_down',
      (glfw.MOD_CONTROL, glfw.KEY_DOWN):  'track_up',

      (glfw.MOD_ALT, glfw.KEY_RIGHT): 'roll_ccw',
      (glfw.MOD_ALT, glfw.KEY_LEFT):  'roll_cw',

      (0,              glfw.KEY_Z): 'zoom_in',
      (glfw.MOD_SHIFT, glfw.KEY_Z): 'zoom_out',

      (0, glfw.KEY_F): 'fit',
      (0, glfw.KEY_O): 'orbit_toggle',
      (0, glfw.KEY_P): 'projection_toggle',
      (0, glfw.KEY_V): 'normal_to',

      (glfw.MOD_CONTROL, glfw.KEY_1): 'view_front',
      (glfw.MOD_CONTROL, glfw.KEY_2): 'view_back',
      (glfw.MOD_CONTROL, glfw.KEY_3): 'view_right',
      (glfw.MOD_CONTROL, glfw.KEY_4): 'view_left',
      (glfw.MOD_CONTROL, glfw.KEY_5): 'view_top',
      (glfw.MOD_CONTROL, glfw.KEY_6): 'view_bottom',
      (glfw.MOD_CONTROL, glfw.KEY_7): 'view_iso'
    }

  def get_command(self, input):
    return self.bindings.get(input)