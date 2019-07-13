class KDTreeNode():
  def __init__(self, aabb, facets = None, left = None, right = None):
    self.aabb = aabb
    self.facets = facets
    self.children = [left, right]

  def is_leaf(self):
    return self.facets is not None

  def intersect(self, ray):
    '''Intersect ray with node and return the ray's t parameter for found intersections. Return None for no intersections.'''
    if not self.aabb.intersect(ray):
      return None

    if self.is_leaf():
      return ray.closest_intersection(self.facets)
    else:
      return self.intersect_children(ray)

  def intersect_children(self, ray):
    '''Intersect ray with children and return the ray's t parameter for found intersections. Return None for no intersections.'''
    intersections = [child.intersect(ray) for child in self.children if child is not None]
    valid_intersections = [inter for inter in intersections if inter is not None]

    return min(valid_intersections) if valid_intersections else None

class KDTree():
  DEPTH_BOUND = 8

  def __init__(self, mesh):
    self.root = self.branch(mesh.aabb, mesh.facets)

  def axis(self, depth):
    return depth % 3

  def split(self, aabb, axis):
    split_plane = aabb.center[axis]
    left, right = aabb.split(axis, split_plane)

    return split_plane, left, right

  def branch(self, aabb, facets, depth = 0) -> KDTreeNode:
    if len(facets) == 0: 
      return None

    if depth >= self.DEPTH_BOUND:
      # Return a leaf node
      return KDTreeNode(aabb, facets=facets)

    axis = self.axis(depth)
    split_plane, left, right = self.split(aabb, axis)

    left_facets  = []
    right_facets = []

    for facet in facets:
      if facet.aabb.min[axis] < split_plane:
        left_facets.append(facet)
      if facet.aabb.max[axis] > split_plane:
        right_facets.append(facet)

    return KDTreeNode(
      aabb,
      left  = self.branch(left, left_facets, depth + 1), 
      right = self.branch(right, right_facets, depth + 1)
    )

  def traverse(self, ray):
    return self.root.intersect(ray)