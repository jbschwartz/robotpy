import time

from typing import Callable, Optional

from .log import logger

class Timer:
  """Multi-use Timer class.

  Can be used to measure code time execution:
    with Timer() as t:
      some_expensive_function()

    print(t.elapsed)

  Can be used call a piece of code at a given frequency:
    interval = Timer(period=2)
    while(True):
      with interval:
        if interval.ready:
          print("Saying hello only after two or more seconds has elapsed since last time")

  Can be used to measure the time since a piece of code was last called:
    event = Timer()
    while(True):
      some_expensive_function()

      with event:
        print(f"Last seen {event.time_since_last}s ago")
  """
  def __init__(self, message: Optional[str] = None, period: Optional[int] = None, get_time: Optional[Callable] = None) -> None:
    self.message    = message
    self.period     = period or 0
    self.get_time   = get_time or time.perf_counter

    self.last_ready = self.get_time() - self.period

    assert self.period >= 0, "Timer period must be >= 0"
    assert (self.get_time() - self.last_ready) > self.period, "Timer ready must always evaluate to true after initialization"

  def __enter__(self) -> 'Timer':
    self.last_entry = self.get_time()

    self.time_since_last = self.last_entry - self.last_ready

    if self.time_since_last > self.period:
      self.ready      = True
      self.last_ready = self.last_entry

    return self

  def __exit__(self, *args) -> None:
    self.elapsed = self.get_time() - self.last_entry

    if self.ready:
      self.ready = False

      if self.message:
        elapsed_string = "{:.3f}".format(self.elapsed)
        logger.info(f'{self.message}: {elapsed_string}s')