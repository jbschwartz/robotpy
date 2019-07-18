class Swizzler:
  def __getattr__(self, name):
    def allow(char):
      if char not in self.__dict__:
        raise AttributeError

      return getattr(self, char)

    return list(map(allow, name))