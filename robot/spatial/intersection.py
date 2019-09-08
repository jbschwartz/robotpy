from collections import namedtuple
from typing      import Any, Optional

class Intersection(namedtuple('Intersection', 't obj previous')):
  __slots__ = ()

  def __new__(cls, t: float, obj: Any, previous: Optional['Intersection'] = None):
    assert t is None or t >= 0, "Intersection can not be behind ray"
    return super().__new__(cls, t, obj, previous)

  @classmethod
  def from_previous(cls, parent: Any, previous: 'Intersection') -> 'Intersection':
    return cls(previous.t, parent, previous)

  @classmethod
  def Miss(cls) -> 'Intersection':
    return cls(None, None, None)

  @property
  def hit(self) -> bool:
    """Returns True if there is a valid Intersection."""
    return self.t is not None

  def closer_than(self, other: 'Intersection') -> bool:
    """Returns True if this Intersection is closer than another Intersection."""
    if self.t is None:
      return False

    return (other.t is None or self.t < other.t)
