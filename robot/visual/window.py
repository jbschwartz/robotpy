import math, numpy, glfw, statistics, sys

from OpenGL.GL import GL_TRUE

from robot.common       import logger, Timer
from robot.utils        import sign
from robot.spatial      import Vector3
from .messaging.emitter import emitter
from .messaging.event   import Event

@emitter
class Window():
  def __init__(self, width, height, title):
    self.width = width
    self.height = height

    self.pause = False
    self.dragging = None
    self.modifiers = 0

    self.show_fps = False

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

    self.emit(Event.KEY, key, action, self.modifiers)

    if key == glfw.KEY_Q and action == glfw.PRESS:
      self.show_fps = not self.show_fps

  def scroll_callback(self, window, x_direction, y_direction):
    self.emit(Event.SCROLL, sign(x_direction), sign(y_direction))

  def mouse_button_callback(self, window, button, action, mods):
    self.emit(Event.CLICK, button, action, self.get_cursor())

    # Record which mouse button is being dragged
    self.dragging = button if action == glfw.PRESS else None

  def cursor_pos_callback(self, window, x, y):
    cursor = Vector3(x, y)

    if self.last_cursor_position:
      cursor_delta = (self.last_cursor_position - cursor)

    self.last_cursor_position = cursor

    event = Event.DRAG if self.dragging is not None else Event.CURSOR
    self.emit(event, self.dragging, cursor, cursor_delta, self.modifiers)

  def window_callback(self, window, width, height):
    self.width = width
    self.height = height
    self.emit(Event.WINDOW_RESIZE, width, height)

  # TODO: Remove this function (in favor of a property?). It's probably not necessary since the cursor_pos callback is constantly updating last_cursor_position
  def get_cursor(self):
    return Vector3(*glfw.get_cursor_pos(self.window), 0)

  def ndc(self, cursor):
    return Vector3(2 * cursor.x / self.width - 1, 1 - 2 * cursor.y / self.height)

  def run(self, fps_limit = None):
    # Send a window resize event so observers are provided the initial window size
    self.window_callback(self.window, *glfw.get_window_size(self.window))

    self.emit(Event.START_RENDERER)

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
        if self.show_fps:
          logger.info(f'FPS: {math.floor(statistics.mean(FPS))}')
        FPS = []

      last_update = now

      self.emit(Event.START_FRAME, delta = delta_update)

      delta_frame = now - last_frame
      if not fps_limit or (fps_limit and delta_frame >= frame_time):
        self.emit(Event.DRAW)
        last_frame = now

      glfw.swap_buffers(self.window)
      glfw.poll_events()