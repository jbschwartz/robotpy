import enum, functools, math

# All of these functions convert quaternion representations to intrinsic euler angles
# This is done by converting the quaternion representation to a partial matrix representation and then to an euler angle representation
# There are two solutions in general (unless the representation is singular, i.e. gimbal lock)

# TODO: Need to handle singular cases
def zyz(r, x, y, z):
  xz = 2 * x * z
  ry = 2 * r * y
  yz = 2 * y * z
  rx = 2 * r * x

  beta = math.acos(1 - 2 * (x ** 2 + y ** 2))

  results = []
  for yp in [beta, -beta]:
    sign = 1 if math.sin(yp) > 0 else -1

    zpp = math.atan2((yz + rx) * sign, (-xz + ry) * sign)
    z = math.atan2((yz - rx) * sign, (xz + ry) * sign)
    results.append([ z, yp, zpp ])

  return results

def zyx(r, x, y, z):
  xy = 2 * x * y
  xz = 2 * x * z
  ry = 2 * r * y
  yz = 2 * y * z
  rx = 2 * r * x
  rz = 2 * r * z

  xSq = x ** 2
  ySq = y ** 2
  zSq = z ** 2

  beta = math.asin(-xz + ry)

  results = []
  for yp in [beta, math.pi + beta]:
    sign = 1 if math.cos(yp) > 0 else -1

    xpp = math.atan2((yz + rx) * sign, (1 - 2 * (xSq + ySq)) * sign)
    z = math.atan2((xy + rz) * sign, (1 - 2 * (ySq + zSq)) * sign)

    results.append([ z, yp, xpp ])

  return results

def _not_implemented(r, x, y, z):
  raise NotImplementedError

class Axes(enum.Enum):
  ZXZ = functools.partial(_not_implemented)
  XYX = functools.partial(_not_implemented)
  YZY = functools.partial(_not_implemented)
  ZYZ = functools.partial(zyz)
  XZX = functools.partial(_not_implemented)
  YXY = functools.partial(_not_implemented)
  XYZ = functools.partial(_not_implemented)
  YZX = functools.partial(_not_implemented)
  ZXY = functools.partial(_not_implemented)
  XZY = functools.partial(_not_implemented)
  ZYX = functools.partial(zyx)
  YXZ = functools.partial(_not_implemented)

  def convert(self, quaternion: 'Quaternion'):
    return self.value(*quaternion)

  def reverse(self):
    reversed_name = self.name[::-1]
    return Axes[reversed_name]

class Order(enum.Enum):
  INTRINSIC = enum.auto()
  EXTRINSIC = enum.auto()

def angles(quaternion: 'Quaternion', axes=Axes.ZYZ, order=Order.INTRINSIC):
  if not isinstance(axes, Axes) or not isinstance(order, Order):
    raise KeyError

  # Take advantage of extrinsic being the reverse axes order intrinsic solution reversed
  if order == Order.EXTRINSIC:
    axes = axes.reverse()

  solutions = axes.convert(quaternion)

  if order == Order.EXTRINSIC:
    solutions = [angles.reverse() for angles in solutions]

  return solutions