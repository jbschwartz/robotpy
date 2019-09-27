from typing import Iterable

from .intersection import Intersection

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

  def closest_intersection(self, collection: Iterable) -> Intersection:
    closest = Intersection.Miss()

    for item in collection:
      # See if the item is intersectable, otherwise ignore it
      if callable(getattr(item, 'intersect', None)):
        x = item.intersect(self)

        if x.closer_than(closest):
          closest = x

    return closest

  def evaluate(self, t):
    '''Return the location along ray given parameter t.'''
    return self.origin + t * self.direction

  def __str__(self):
    return f"{self.origin} + t * {self.direction}"