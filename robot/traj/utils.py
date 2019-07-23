def interpolate(start: 'Vector3', end: 'Vector3', t: float):
  '''Interpolate between start and end with 0 <= t <= 1.'''
  slope = end - start
  return slope * t + start