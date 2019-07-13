DEPTH_BOUND = 8

class KDTreeNode():
  def __init__(self, aabb, facets = None, left = None, right = None):
    self.aabb = aabb
    self.facets = facets
    self.children = [left, right]

  def is_leaf(self):
    return self.facets is not None

  def axis(self, depth):
    return depth % 3

  def split_aabb(self, axis):
    split_plane = self.aabb.center[axis]
    left, right = self.aabb.split(axis, split_plane)

    return split_plane, left, right

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
    if len(self.facets) == 0: 
      return None

    if depth >= DEPTH_BOUND:
      return

    axis = self.axis(depth)

    # split_plane, *boxes = self.split_aabb(axis)

    # *all_facets = self.split_facets(split_plane, facets)

    # self.children = [KDTreeNode(box, facets) for box, facets in zip(boxes, all_facets)]

    # if any(filter(lambda child: child is not None, self.children))
    #   self.facets = None

    split_plane, left, right = self.split_aabb(axis)

    # left_facets  = []
    # right_facets = []

    left_facets, right_facets = self.split_facets(axis, split_plane)

    left = KDTreeNode(left, left_facets)
    right = KDTreeNode(right, right_facets)

    self.children = [left, right]

    if left or right:
      self.facets = None

    left.branch(depth + 1),
    right.branch(depth + 1)

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