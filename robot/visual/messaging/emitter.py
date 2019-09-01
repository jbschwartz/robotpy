from .event    import Event
from .registry import registry

def emitter(cls):
  """Emitter class decorator allows instance to call self.emit."""
  def emit(self, event: Event, *args, **kwargs) -> None:
    """Emit an event to all registered listeners."""
    listeners = registry.get(event)
    if listeners:
      for listener in listeners:
        # TODO: Maybe use some sort of introspection technique to see if the listener wants certain parameters
        # This would eliminate the need for all listeners to declare function parameters, even if they're unused
        listener(*args, **kwargs)

  cls.emit = emit

  return cls
