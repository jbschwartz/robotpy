class Ray():
  def __init__(self, origin, direction):
    self.origin = origin
    # TODO: What about a zero-length direction vector?
    self.direction = direction.normalize()

  def closest_intersection(self, collection):
    closest = None

    for item in collection:
      try:
        t = item.intersect(self)
        
        if t and (closest is None or t < closest):
          closest = t
      except AttributeError:
        # Ignore any items in the collection that cannot be intersected
        continue

    return closest

  def evaluate(self, t):
    '''Return the location along ray given parameter t.'''
    return self.origin + t * self.direction

  def __str__(self):
    return f"{self.origin} + t * {self.direction}"