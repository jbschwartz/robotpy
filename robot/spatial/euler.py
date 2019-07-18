import math

# All of these functions convert quaternion representations to intrinsic euler angles
# This is done by converting the quaternion representation to a partial matrix representation and then to an euler angle representation
# There are two solutions in general (unless the representation is singular, i.e. gimbal lock)

# TODO: Need to handle singular cases

allSequences = ['zxz', 'xyx', 'yzy', 'zyz', 'xzx', 'yxy', 'xyz', 'yzx', 'zxy', 'xzy', 'zyx', 'yxz']

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