import glfw, sys

from OpenGL.GL import GL_FALSE

from robot.common.timer         import Timer
from robot.spatial.vector3      import Vector3
from robot.visual.window_events import WindowEvents

class Window():
  def __init__(self, x, y, title):
    self.observers = []
    self.pause = False
    self.dragging = False

    if not glfw.init():
      sys.exit('GLFW initialization failed')
    
    self.window_hints()

    with Timer('Create Window') as t:
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
    self.emit(WindowEvents.KEY, key, action)

    # This may be better suited in some sort of simulation controller class
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
      self.pause = not self.pause

  def scroll_callback(self, window, x_direction, y_direction):
    self.emit(WindowEvents.SCROLL, Vector3(x_direction, y_direction))

  def mouse_button_callback(self, window, button, action, mods):
    if button is glfw.MOUSE_BUTTON_LEFT:
      if action == glfw.PRESS:
        cursor_position = Vector3(*glfw.get_cursor_pos(self.window), 0)
        self.emit(WindowEvents.CLICK, cursor_position, action)

      self.dragging = action == glfw.PRESS

  def cursor_pos_callback(self, window, x, y):
    if self.dragging:
      self.emit(WindowEvents.CURSOR, Vector3(x, y, 0))

  def register_observer(self, observer, events = []):
    # If valid_events is empty, subscribe the observer to all events
    self.observers.append((observer, events))

  def emit(self, event_type, *args, **kwargs):
    for observer, valid_events in self.observers:
      if not valid_events or event_type in valid_events:
        observer.notify(event_type, *args, **kwargs)

  def run(self, fps_limit = None):
    with Timer('START_RENDERER') as t:
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




