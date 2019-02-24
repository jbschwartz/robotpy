import math

from .. import constant

def is_singular(r, s, upper_arm_length, fore_arm_length):
  '''
  A 2R manipulator is singular if the target point coincides with the shoulder axis
  '''
  return math.isclose(r, 0) and math.isclose(s, 0) and math.isclose(upper_arm_length, fore_arm_length)

def solve_shoulder(r, s, upper_arm_length, fore_arm_length, elbow):
  '''
  Calculate the shoulder (joint 1) angles from elbow angle.

  The problem has been projected onto a plane (planar 2R robot).

  Does not do any checking for points out of reach as there would be no valid elbow angle to pass in.
  '''

  if is_singular(r, s, upper_arm_length, fore_arm_length): 
    return [ constant.SINGULAR ]

  angles = []

  phi = math.atan2(s, r)

  for angle in [elbow, -elbow]:
    shoulder = phi - math.atan2(fore_arm_length * math.sin(angle), upper_arm_length + fore_arm_length * math.cos(angle))
    angles.append(shoulder)

    # If angle is either 0 or Pi, then both elbow angles will generate the same shoulder angle.
    if math.isclose(angle, 0) or math.isclose(angle, math.pi):
      break

  return angles
