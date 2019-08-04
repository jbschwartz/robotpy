from robot.spatial import euler, Transform

def solve_wrist(target : Transform, arm_angles : list, robot : 'Serial'):
  '''
  Get joint angles from a given target (inverse kinematics)

  This function decouples the position and orientation of the robot into two separate problems
  '''
  solutions = []

  for angle_set in arm_angles:
    # Get current end effector pose generated by moving the arm to provided solution set angles
    # We use the equation by forward kinematics: Current Flange Frame * Delta * Tool Frame = Target
    ee_flange = robot.pose_at(angle_set + [0] * 3)

    if robot.tool is not None:
      ee_flange *= robot.tool._tip.inverse()

    # Get "difference" between current end effector pose and the target pose
    # That is: Delta = Current Flange Inverse * Target * Tool Frame Inverse
    delta = ee_flange.inverse() * target

    if robot.tool is not None:
      delta *= robot.tool._tip.inverse()

    # Must be intrinsic ZYZ based on mechanical configuration of spherical wrist
    #   Axis 4 rotates about Z, Axis 5 rotates about Y, Axis 6 rotates about Z
    # There are at least two solutions
    wrist_sets = euler.angles(delta.rotation(), axes=euler.Axes.ZYZ, order=euler.Order.INTRINSIC)

    solutions.extend([angle_set + wrist_set for wrist_set in wrist_sets])

  return solutions