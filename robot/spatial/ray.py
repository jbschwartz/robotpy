class Ray():
  def __init__(self, origin, direction):
    self.origin = origin
    # TODO: What about a zero-length direction vector?
    self.direction = direction.normalize()

  def evaluate(self, t):
    '''Return the location along ray given parameter t.'''
    return self.origin + t * self.direction

  def __str__(self):
    return f"{self.origin} + t * {self.direction}"