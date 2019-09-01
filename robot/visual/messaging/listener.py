from typing import Callable

from .event    import Event
from .registry import registry

# TODO: Maybe allow the listen decorator to accept parameters that allow the function to listen conditionally
# e.g. @listen(Event.KEY, glfw.KEY_SPACE) would only listen to spacebar
def listen(*events: Event) -> Callable:
  def decorator_listen(func: Callable) -> Callable:
    if events:
      func._listen_to = events
    return func
  return decorator_listen

def listener(cls):
  """Listener class decorator registers all event handling methods."""
  class ListenerWrapper(cls):
    def __init__(self, *args, **kwargs) -> None:
      self._register_listeners()
      super().__init__(*args, **kwargs)

    def _register_listeners(self) -> None:
      """Add methods with `_listen_to` attribute to the Event listener registry."""
      for name, method in cls.__dict__.items():
        if getattr(method, '_listen_to', None):
          listener = getattr(self, name)
          for event in method._listen_to:
            if registry.get(event):
              registry[event].append(listener)
            else:
              registry[event] = [listener]

  return ListenerWrapper