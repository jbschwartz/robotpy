from collections import namedtuple
from typing      import Any, Optional

class Intersection(namedtuple('Intersection', 't obj')):
  __slots__ = ()

  # TODO: It may be necessary to include the chain of intersections that occur to the caller.
  # e.g. Facet -> Mesh -> Link -> Serial
  # This could maybe be implemented with a `previous` attribute on the tuple
  # i.e. __new__(..., previous: 'Intersection')
  def __new__(cls, t: Optional[float], obj: Optional[Any]):
    assert t is None or t >= 0, "Intersection can not be behind ray"
    return super().__new__(cls, t, obj)

  @classmethod
  def Miss(cls) -> 'Intersection':
    return cls(None, None)

  @property
  def hit(self) -> bool:
    """Returns True if there is a valid Intersection."""
    return self.t is not None

  def closer_than(self, other: 'Intersection') -> bool:
    """Returns True if this Intersection is closer than another Intersection."""
    if self.t is None:
      return False

    return (other.t is None or self.t < other.t)
