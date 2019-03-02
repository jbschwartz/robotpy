import math

from .. import constant, utils

def solve_waist(x, y, wristOffset = 0):
  '''
  Calculate the waist (joint 0) angles with a shoulder-wrist offset
  '''
  alpha = 0

  if not math.isclose(wristOffset, 0):
    # Shoulder-wrist offsets create potential for unreachable locations (so we check)
    #    A point is unreachable if x^2 + y^2 < d^2,
    #    i.e. if the point is "inside" the (circle produced by the) offset wrist
    delta = x ** 2 + y ** 2 - wristOffset ** 2
    if delta < 0: 
      return [] # No solution

    alpha = math.atan2(wristOffset, math.sqrt(delta))
  else:
    shoulderIsSingular = math.isclose(x, 0) and math.isclose(y, 0)
    if shoulderIsSingular: 
      return [ constant.SINGULAR ] # Infinite possible solutions

  phi = math.atan2(y, x)

  # Give solutions for both "left" and "right" shoulder configurations
  # Constrain solutions to (-PI, PI] as joint limits are typically symmetric about zero
  first = utils.clamp_angle(phi - alpha)
  second = utils.clamp_angle(phi + alpha + math.pi)

  return [ first, second ]