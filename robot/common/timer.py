import time

from .log import logger

class Timer:
  def __init__(self, message = None):
    self.message = message

  def __enter__(self):
    self.start = time.perf_counter()
    return self

  def __exit__(self, *args):
    self.end = time.perf_counter()
    self.elapsed = self.end - self.start

    if self.message:
      logger.info(f'{self.message}: {"{:.3f}".format(self.elapsed)}')