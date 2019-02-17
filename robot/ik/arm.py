import math

from ..spatial import Vector3

from .waist import solveWaist
from .elbow import solveElbow
from .shoulder import solveShoulder

def rsCoordinates(wristCenter : Vector3, shoulderWristOffset, shoulderZOffset):
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

  r = math.sqrt(wristCenter.x ** 2 + wristCenter.y ** 2 - shoulderWristOffset ** 2)
  s = wristCenter.z - shoulderZOffset

  return [ r, s ]

def solveArm(wristCenter : Vector3, upperArmLength, foreArmLength, shoulderWristOffset, shoulderZOffset):
  '''
  Get solutions for the first three joints of a canonical arm
  '''

  waist = solveWaist(wristCenter.x, wristCenter.y, shoulderWristOffset)
  if not waist: 
    return []

  r, s = rsCoordinates(wristCenter, shoulderWristOffset, shoulderZOffset)

  elbow = solveElbow(r, s, upperArmLength, foreArmLength)
  if math.isnan(elbow): 
    return []

  shoulder = solveShoulder(r, s, upperArmLength, foreArmLength, elbow)
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

