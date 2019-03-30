import sys

import glfw

from OpenGL.GL import GL_FALSE

from .window_events import WindowEvents

from ..spatial.vector3 import Vector3

class Window():
  def __init__(self, x, y, title):
    self.observers = []
    self.pause = False
    self.track_mouse = False
    self.last_mouse_position = None

    if not glfw.init():
      sys.exit('GLFW initialization failed')
    
    self.window_hints()

    self.window = glfw.create_window(x, y, title, None, None)
    
    if not self.window:
      glfw.terminate()
      sys.exit('GLFW create window failed')

    self.set_callbacks()

    glfw.make_context_current(self.window)

  def window_hints(self):
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
    glfw.window_hint(glfw.SAMPLES, 4)

  def set_callbacks(self):
    glfw.set_window_size_callback(self.window, lambda *args: self.emit(WindowEvents.WINDOW_RESIZE, *args))
    glfw.set_key_callback(self.window, self.key_callback)
    glfw.set_scroll_callback(self.window, self.scroll_callback)
    glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
    glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)

  def key_callback(self, window, key, scancode, action, mods):
    # TODO: Key bindings class?
    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT] and action in [glfw.PRESS, glfw.REPEAT]:
      x_direction = 1 if key == glfw.KEY_RIGHT else -1
      self.emit(WindowEvents.ORBIT, Vector3(x_direction, 0, 0))

    if key == glfw.KEY_SPACE and action == glfw.PRESS:
      self.pause = not self.pause

  def scroll_callback(self, window, x_direction, y_direction):
    if y_direction:
      self.emit(WindowEvents.ZOOM, y_direction)
    if x_direction:
      self.emit(WindowEvents.ORBIT, Vector3(x_direction, 0, 0))

  def mouse_button_callback(self, window, button, action, mods):
    if button is glfw.MOUSE_BUTTON_LEFT:
      self.track_mouse = True if action == glfw.PRESS else False

  def cursor_pos_callback(self, window, x, y):
    current_mouse_position = Vector3(x, y)

    if self.track_mouse:
      delta = current_mouse_position - self.last_mouse_position
      print(delta)
      self.emit(WindowEvents.ORBIT, delta)

    self.last_mouse_position = current_mouse_position

  def register_observer(self, observer, events = []):
    self.observers.append((observer, events))

  def emit(self, event_type, *args, **kwargs):
    for observer, valid_events in self.observers:
      if not valid_events or event_type in valid_events:
        observer.notify(event_type, *args, **kwargs)

  def run(self, fps_limit = None):
    self.emit(WindowEvents.START_RENDERER)

    now = glfw.get_time()
    last_frame = now
    last_update = now

    frame_time = 0 if not fps_limit else 1 / fps_limit 

    while not glfw.window_should_close(self.window):
      now = glfw.get_time()
      delta_update =  now - last_update
      last_update = now

      if not self.pause:
        self.emit(WindowEvents.UPDATE, delta = delta_update)

      self.emit(WindowEvents.START_FRAME)
      
      delta_frame = now - last_frame
      if not fps_limit or (fps_limit and delta_frame >= frame_time):
        self.emit(WindowEvents.DRAW)
        last_frame = now
      
      self.emit(WindowEvents.END_FRAME)

      glfw.swap_buffers(self.window)
      glfw.poll_events()

    self.emit(WindowEvents.END_RENDERER)




