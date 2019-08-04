import math

from robot.spatial import Transform
from .arm          import solve_arm
from .wrist        import solve_wrist

def redundant_solutions(solutions, robot):
  # TODO: This can probably be more concise
  # TODO: And this is actually wrong for robots which have more than one joint with multiple revolutions.
  #   The number of additional solutions should be multiplicative (but it's not)
  # TODO: Replace solutions lists with a tree structure. Lists can be generated with DFS
  additional_solutions = []
  for index, joint in enumerate(robot.joints):
    travel_in_revs = joint.travel_in_revs
    if travel_in_revs >= 1:
      for angle_set in solutions:
        for x in range(1, travel_in_revs + 1):
          newHigh = angle_set.copy()
          newHigh[index] += 2 * math.pi * x
          newLow = angle_set.copy()
          newLow[index] -= 2 * math.pi * x
          additional_solutions.append(newHigh)
          additional_solutions.append(newLow)
  return additional_solutions

def solve_angles(target : Transform, robot):
  '''
  Get joint angles from a given target (inverse kinematics)

  This function decouples the position and orientation of the robot into two separate problems
  '''
  # Transform end-effector tip frame to wrist center frame
  wrist_center = robot.wrist_center(target)

  solutions = solve_arm(
    wrist_center,
    robot.upper_arm_length(),
    robot.fore_arm_length(),
    robot.shoulder_wrist_offset(),
    robot.shoulder_z()
  )

  robot.transform_to_robot(solutions)

  solutions = solve_wrist(target, solutions, robot)

  # Get additional redundant solutions from joints that can rotate more than one full rotation
  additional_solutions = redundant_solutions(solutions, robot)

  solutions.extend(additional_solutions)

  # Remove solutions if beyond joint limits.
  # Doing this at the very end is not as efficient but does make the code more concise
  #   A more efficient way would be to check the limit at the time the joint angle is solved
  #   This prevents solutions from being calculated for infeasible joint angles
  solutions = list(filter(robot.within_limits, solutions))

  return solutions