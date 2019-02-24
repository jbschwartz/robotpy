import math

from ..spatial import Vector3

from .waist import solve_waist
from .elbow import solve_elbow
from .shoulder import solve_shoulder

def rs_coordinates(wrist_center : Vector3, shoulder_wrist_offset, shoulder_z_offset):
  '''
  Project a point (usually wrist center) in three dimension space onto the two dimension RS plane
  
  This turns the problem into solving a 2R manipulator.
  '''

  #             (Side)                                (Top)
  #               ^ Z          Target (x, y, z)        ^ Y
  #               |           /    => (r, s)           |
  #               ^ S (O)====X                         |
  #     Shoulder  |  // \                              |/---- r ----/
  #             \ |//    Elbow                 ---^--- (O)==(O)=====X (x, y)
  #    --^---    (O)-----------> R                |    ||       _ /
  #   offset    =====                           offset ||   _ /   \
  #      |      || ||                             |    || /        sqrt(x^2 + y^2)
  #   ---V--- ----|---------> X                ---V--- (O)-----------> X 

  r = math.sqrt(wrist_center.x ** 2 + wrist_center.y ** 2 - shoulder_wrist_offset ** 2)
  s = wrist_center.z - shoulder_z_offset

  return [ r, s ]

def solve_arm(wrist_center : Vector3, upper_arm_length, fore_arm_length, shoulder_wrist_offset, shoulder_z_offset):
  '''
  Get solutions for the first three joints of a canonical arm
  '''

  waist = solve_waist(wrist_center.x, wrist_center.y, shoulder_wrist_offset)
  if not waist: 
    return []

  r, s = rs_coordinates(wrist_center, shoulder_wrist_offset, shoulder_z_offset)

  elbow = solve_elbow(r, s, upper_arm_length, fore_arm_length)
  if math.isnan(elbow): 
    return []

  shoulder = solve_shoulder(r, s, upper_arm_length, fore_arm_length, elbow)
  if not shoulder: 
    return []

  if len(shoulder) == 1:
    shoulder.append(shoulder[0])

  # The elbow can have an up and down configuration if it is not colinear with the shoulder
  # Flip the shoulder handedness for the second waist solution
  if math.isclose(elbow, 0) or math.isclose(elbow, math.pi):
    return [ [ waist[0], shoulder[0], elbow ], [ waist[1], math.pi - shoulder[1], elbow ] ]
  else:
    # When the shoulder switches handedness, the elbow flips configuration
    return [
      [ waist[0], shoulder[0], elbow ],
      [ waist[0], shoulder[1], -elbow ],
      [ waist[1], math.pi - shoulder[0], -elbow ],
      [ waist[1], math.pi - shoulder[1], elbow ],
    ]

