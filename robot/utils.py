import math

def clamp_angle(angle):
  '''
  Clamp angle to the range (-pi, pi]
  '''
  revolution = 2 * math.pi

  while angle > math.pi:
    angle -= revolution
  while angle <= -math.pi:
    angle += revolution

  return angle

def safe_acos(value):
  '''
  Checks to make sure that small floating point representation "errors" (e.g. 1.00000000002) do not raise ValueErrors
  '''
  if math.isclose(value, 1):
    return 0
  elif math.isclose(value, -1):
    return math.pi
  else:
    return math.acos(value)

def raise_if(should_raise: bool, exception_type: Exception):
  if should_raise:
    raise exception_type