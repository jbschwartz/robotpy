from typing import Callable

from .event    import Event
from .registry import registry

def listen(*events: Event) -> Callable:
  def decorator_listen(func: Callable) -> Callable:
    if events:
      func._listen_to = events
    return func
  return decorator_listen

def listener(cls):
  """Listener class decorator registers all event handling methods."""
  class ListenerWrapper:
    def __init__(self, *args, **kwargs) -> None:
      self.wrapped = cls(*args, **kwargs)
      self._register_listeners()

    def _register_listeners(self) -> None:
      """Add methods with `_listen_to` attribute to the Event listener registry."""
      for name, method in cls.__dict__.items():
        if getattr(method, '_listen_to', None):
          listener = getattr(self.wrapped, name)
          for event in method._listen_to:
            if registry.get(event):
              registry[event].append(listener)
            else:
              registry[event] = [listener]

    def __getattr__(self, attr):
      return getattr(self.wrapped, attr)

  return ListenerWrapper