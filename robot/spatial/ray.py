class Ray():
  def __init__(self, origin, direction):
    self.origin = origin
    # TODO: What about a zero-length direction vector?
    self.direction = direction.normalize()

  def transform(self, transform: 'Transform') -> 'Ray':
    '''Return a new transformed ray.'''
    new_origin    = self.origin.transform(transform, as_type="point")
    new_direction = self.direction.transform(transform, as_type="vector")

    return Ray(new_origin, new_direction)

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