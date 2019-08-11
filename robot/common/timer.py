import time

from .log import logger

class Timer:
  def __init__(self, message = None):
    self.message = message

  def __enter__(self):
    self.start = time.clock()
    return self

  def __exit__(self, *args):
    self.end = time.clock()
    self.elapsed = self.end - self.start

    if self.message:
      logger.info(f'{self.message}: {self.elapsed}')