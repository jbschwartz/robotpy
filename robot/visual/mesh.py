import math

from robot.spatial.aabb       import AABB 
from robot.spatial.ray        import Ray 
from robot.spatial.vector3    import Vector3 

class Mesh:
  def __init__(self, name = None):
    self.name = name
    self.facets = []
    self.aabb = AABB()
    
    self._accelerator = None

    self.properties = {
      'com':     None,
      'moments': None,
      'volume':  None
    }

  @property
  def accelerator(self):
    return self._accelerator

  @accelerator.setter
  def accelerator(self, accelerator):
    self._accelerator = accelerator(self)

  def vertices(self):
    '''Iterable list of mesh vertices returned grouped by facet.'''
    for facet in self.facets:
      yield facet.vertices[0]
      yield facet.vertices[1]
      yield facet.vertices[2]

  @property
  def center_of_mass(self):
    if not self.properties['com']:
      self.calculate_properties()

    return self.properties['com']

  @property
  def moments(self):
    if not self.properties['moments']:
      self.calculate_properties()

    return self.properties['moments']

  @property
  def volume(self):
    if not self.properties['volume']:
      self.calculate_properties()

    return self.properties['volume']

  def calculate_properties(self):
    '''Calculate the volume, moments, and center of mass (assuming uniform density) of the mesh.'''
    def tetrahedron_volume(facet):
      '''Volume of a tetrahedron created by the three facet vertices and origin.'''
      a, b, c = facet.vertices
      return (a * (b % c)) / 6

    def tetrahedron_centroid(f):
      '''Volume of a tetrahedron created by the three facet vertices and origin.'''
      return sum(f.vertices, Vector3()) / 4

    mesh_volume   = 0
    mesh_centroid = Vector3()
    
    moments = {
      'ixx': 0,
      'iyy': 0,
      'izz': 0,
      'ixy': 0,
      'iyz': 0,
      'ixz': 0
    }
    # Find the contribution of all created tetrahedrons: com = sum(dv * r) / V where:
    #   dv is the volume of the tetrahedron, 
    #   r is the centroid of the tetrahedron, and 
    #   V is the volume of the whole mesh
    for facet in self.facets:
        volume = tetrahedron_volume(facet)
        centroid = tetrahedron_centroid(facet)

        mesh_volume   += volume
        mesh_centroid += volume * centroid

        sq = Vector3(
          centroid.x * centroid.x,
          centroid.y * centroid.y,
          centroid.z * centroid.z
        )

        moments['ixx'] += (sq.y + sq.z) * volume
        moments['iyy'] += (sq.x + sq.z) * volume
        moments['izz'] += (sq.x + sq.y) * volume
        moments['ixy'] -= (centroid.x * centroid.y * volume)
        moments['iyz'] -= (centroid.y * centroid.z * volume)
        moments['ixz'] -= (centroid.x * centroid.z * volume)

    self.properties['com']     = mesh_centroid / mesh_volume
    self.properties['volume']  = mesh_volume
    self.properties['moments'] = moments

  def append(self, facet):
    '''Add a facet to the mesh.'''
    self.aabb.extend(*facet.vertices)

    self.facets.append(facet)
    
    if self.accelerator:
      self.accelerator.update(self, facet)

  def intersect(self, local_ray : Ray):
    '''Intersect a ray with mesh and return the ray's t parameter for found intersections. Return None for no intersections.'''
    if self.accelerator:
      return self.accelerator.intersect(local_ray)
    else:
      # Otherwise we brute force the computation
      return local_ray.closest_intersection(self.facets)