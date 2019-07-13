DEPTH_BOUND = 8

class KDTreeNode():
  def __init__(self, aabb, facets = None, left = None, right = None):
    self.aabb = aabb
    self.facets = facets
    self.children = [left, right]

  def is_leaf(self):
    return self.facets is not None

  def can_branch(self, depth):
    if len(self.facets) == 0 or depth >= DEPTH_BOUND:
      return False

    return True

  def splitting_plane(self, depth):
    axis = depth % 3
    plane_value = self.aabb.center[axis]

    return axis, plane_value

  def split_facets(self, axis, split_plane):
    '''Split the list of facets in the node into left and right lists based on splitting axis and plane'''
    left, right = [], []

    for facet in self.facets:
      # Check minimum bound on left and maximum bound on right so that the triangle is not included in any list twice
      # This covers both scenarios: facets belonging to one side only or both sides
      if facet.aabb.min[axis] < split_plane:
        left.append(facet)
      if facet.aabb.max[axis] > split_plane:
        right.append(facet)
    
    return left, right

  def branch(self, depth = 0):
    if not self.can_branch(depth):
      return

    splitting_plane = self.splitting_plane(depth)

    boxes = self.aabb.split(*splitting_plane)

    facet_groups = self.split_facets(*splitting_plane)

    self.children = [KDTreeNode(aabb, facets) for aabb, facets in zip(boxes, facet_groups)]

    for child in self.children:
      if child:
        self.facets = None

      child.branch(depth + 1)

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
  def __init__(self, mesh):
    self.root = KDTreeNode(mesh.aabb, mesh.facets)

  def construct(self):
    self.root.branch()

  def traverse(self, ray):
    return self.root.intersect(ray)