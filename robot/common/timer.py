import time

class Timer:
  def __init__(self, message = None, show_message = True):
    self.message = message
    self.show_message = show_message

  def __enter__(self):
    self.start = time.clock()
    return self

  def __exit__(self, *args):
    self.end = time.clock()
    self.elapsed = self.end - self.start
    
    if self.message and self.show_message:
      print(f'{self.message}: {self.elapsed}')