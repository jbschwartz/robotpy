import math

def clampAngle(angle):
  '''
  Clamp angle to the range (-pi, pi]
  '''
  revolution = 2 * math.pi

  while angle > math.pi:
    angle -= revolution
  while angle <= -math.pi:
    angle += revolution

  return angle