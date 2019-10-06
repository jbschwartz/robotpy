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

def add_listener(event, listener) -> None:
  if event in registry:
    registry[event].append(listener)
  else:
    registry[event] = [listener]

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

          if len(method._listen_to) == 1:
            add_listener(method._listen_to[0], listener)
          else:
            for event in method._listen_to:
              # Use the binding of default function parameters to counteract
              # the late binding closures
              def multi_event_handler(e = event, l = listener):
                def handler(*args, **kwargs):
                  # If more than one event is registered to this listener,
                  # the listener expects to receive the event first
                  l(e, *args, **kwargs)
                return handler

              add_listener(event, multi_event_handler())

  ListenerWrapper.__name__ = cls.__name__

  return ListenerWrapper