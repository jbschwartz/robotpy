import math

def solve_elbow(r, s, upper_arm_length, fore_arm_length):
  '''
  Calculate one elbow (joint 2) angle.

  Callers will negate the returned value to get the other elbow configuration
  '''

  # Law of cosines
  cosTheta = (r ** 2 + s ** 2 - upper_arm_length ** 2 - fore_arm_length ** 2) / (2 * upper_arm_length * fore_arm_length)

  # Use atan instead of acos as atan performs better for very small angle values
  # This will return nan if the target location is unreachable (i.e. cosTheta is outside the range [-1, 1])
  # TODO: Decide if it should instead pass the exception along
  try:
    result = math.atan2(math.sqrt(1 - cosTheta * cosTheta), cosTheta)
    return result
  except:
    return math.nan