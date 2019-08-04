from .window_event import WindowEvent

class Observer:
  def notify(self, event, *args, **kwargs):
    # Use the WindowEvent enum to whitelist the possible attributes
    if isinstance(event, WindowEvent):
      # See if the object has a function with the same name as event
      fn = getattr(self, str(event), None)

      if fn:
        fn(*args, **kwargs)