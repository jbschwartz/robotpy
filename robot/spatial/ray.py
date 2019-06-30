class Ray():
  def __init__(self, origin, direction):
    self.origin = origin
    self.direction = direction

  def __str__(self):
    return f"{self.origin} + t * {self.direction}"