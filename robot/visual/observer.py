from robot.visual.window_events import WindowEvents

class Observer:
  def notify(self, event, *args, **kwargs):
    # Use the WindowEvents enum to whitelist the possible attributes
    if isinstance(event, WindowEvents):
      # See if the object has a function with the same name as event
      fn = getattr(self, str(event), None)

      if fn:
        fn(*args, **kwargs)