import math

from ..spatial import Transform, Vector3, Quaternion, Dual

# TODO: Generalize this class to potentially handle prismatic case

class Joint:
  def __init__(self, alpha, a, theta, d, limits):
    self.dh = {
      'alpha': alpha,
      'a': a,
      'theta': theta,
      'd': d
    }

    self.alpha = alpha
    self.a = a
    self.theta = theta
    self.d = d

    self.limits = {}
    if all(key in limits for key in ('low', 'high')):
      if limits['low'] > limits['high']:
        limits['low'], limits['high'] = limits['high'], limits['low']
      self.limits['low'] = limits['low']
      self.limits['high'] = limits['high']
    else:
      raise KeyError()

    # Precompute quaternions for the joint transform
    self.alpha = Quaternion(axis = Vector3(1, 0, 0), angle = self.dh['alpha'])
    self.a = Quaternion(0, self.dh['a'], 0, 0)
    self.a_alpha = self.a * self.alpha
    self.d = Quaternion(0, 0, 0, self.dh['d'])

  def transform(self, q):
    '''
    Create transformation from Denavit-Hartenberg parameters
    
    Transform = Translate_z(d) * Rotate_z(theta) * Translate_x(a) * Rotate_x(alpha)
    '''

    sum = self.dh['theta'] + q
    theta = Quaternion(axis = Vector3(0, 0, 1), angle = sum)
    r = theta * self.alpha
    dual = Dual(r, 0.5 * (theta * self.a_alpha + self.d * r))
  
    return Transform(dual = dual)

  def num_revolutions(self):
    return math.floor((self.limits['high'] - self.limits['low']) / (2 * math.pi))
