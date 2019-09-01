from typing import Any

class FrozenDict():
  """Dictionary that does not allow keys to be added to after initialization."""
  def __init__(self, d: dict) -> None:
    for key, value in d.items():
      self.__dict__[key] = value

  def __setattr__(self, name: str, value: Any) -> None:
    if hasattr(self, name):
      self.__dict__[name] = value
    else:
      raise AttributeError