import math, numpy, glfw, statistics, sys

from OpenGL.GL import GL_TRUE

from robot.common.timer         import Timer
from robot.spatial.vector3      import Vector3
from robot.visual.window_event  import WindowEvent

class Window():
  def __init__(self, width, height, title):
    self.width = width
    self.height = height

    self.observers = []
    self.pause = False
    self.dragging = None
    self.modifiers = 0

    if not glfw.init():
      sys.exit('GLFW initialization failed')

    self.window_hints()

    with Timer('Create Window') as t:
      self.window = glfw.create_window(self.width, self.height, title, None, None)

    if not self.window:
      glfw.terminate()
      sys.exit('GLFW create window failed')

    self.set_callbacks()

    glfw.make_context_current(self.window)
    glfw.swap_interval(0)

    self.last_cursor_position = self.get_cursor()

  def window_hints(self):
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.RESIZABLE, GL_TRUE)
    glfw.window_hint(glfw.SAMPLES, 4)

  def set_callbacks(self):
    glfw.set_window_size_callback(self.window, self.window_callback)
    glfw.set_key_callback(self.window, self.key_callback)
    glfw.set_scroll_callback(self.window, self.scroll_callback)
    glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
    glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)

  def key_callback(self, window, key, scancode, action, mods):
    self.modifiers = mods

    self.emit(WindowEvent.KEY, key, action, self.modifiers)

    # This may be better suited in some sort of simulation controller class
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
      self.pause = not self.pause

  def scroll_callback(self, window, x_direction, y_direction):
    self.emit(WindowEvent.SCROLL, numpy.sign(x_direction), numpy.sign(y_direction))

  def mouse_button_callback(self, window, button, action, mods):
    self.emit(WindowEvent.CLICK, button, action, self.get_cursor())

    # Record which mouse button is being dragged
    self.dragging = button if action == glfw.PRESS else None

  def cursor_pos_callback(self, window, x, y):
    cursor = Vector3(x, y)

    if self.last_cursor_position:
      cursor_delta = (self.last_cursor_position - cursor)

    self.last_cursor_position = cursor

    event = WindowEvent.DRAG if self.dragging is not None else WindowEvent.CURSOR
    self.emit(event, self.dragging, cursor, cursor_delta, self.modifiers)

  def window_callback(self, window, width, height):
    self.width = width
    self.height = height
    self.emit(WindowEvent.WINDOW_RESIZE, width, height)

  # TODO: Remove this function (in favor of a property?). It's probably not necessary since the cursor_pos callback is constantly updating last_cursor_position
  def get_cursor(self):
    return Vector3(*glfw.get_cursor_pos(self.window), 0)

  def ndc(self, cursor):
    return Vector3(2 * cursor.x / self.width - 1, 1 - 2 * cursor.y / self.height)

  def register_observer(self, observer, events = []):
    # If valid_events is empty, subscribe the observer to all events
    self.observers.append((observer, events))

  def emit(self, event_type, *args, **kwargs):
    for observer, valid_events in self.observers:
      if not valid_events or event_type in valid_events:
        observer.notify(event_type, *args, **kwargs)

  def run(self, fps_limit = None):
    # Send a window resize event so observers are provided the initial window size
    self.window_callback(self.window, *glfw.get_window_size(self.window))

    with Timer('START_RENDERER') as t:
      self.emit(WindowEvent.START_RENDERER)

    now = glfw.get_time()
    last_frame = now
    last_update = now

    frame_time = 0 if not fps_limit else 1 / fps_limit

    FPS = []

    while not glfw.window_should_close(self.window):
      now = glfw.get_time()
      delta_update =  now - last_update

      if len(FPS) < 20:
        FPS.append(1 / delta_update)
      else:
        print('FPS: ', math.floor(statistics.mean(FPS)))
        FPS = []

      last_update = now

      if not self.pause:
        self.emit(WindowEvent.UPDATE, delta = delta_update)

      self.emit(WindowEvent.START_FRAME)

      delta_frame = now - last_frame
      if not fps_limit or (fps_limit and delta_frame >= frame_time):
        self.emit(WindowEvent.DRAW)
        last_frame = now

      self.emit(WindowEvent.END_FRAME)

      glfw.swap_buffers(self.window)
      glfw.poll_events()

    self.emit(WindowEvent.END_RENDERER)




