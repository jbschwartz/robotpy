class KDTreeNode():
  def __init__(self, aabb, facets = None, left = None, right = None):
    self.aabb = aabb
    self.facets = facets
    self.left = left
    self.right = right

  def intersect(self, ray):
    if self.aabb.intersect(ray):
      if self.facets is not None:
        # Leaf node
        return ray.closest_intersection(self.facets)
      else:
        t_left = None
        t_right = None

        if self.left:
          t_left = self.left.intersect(ray)

        if self.right:
          t_right = self.right.intersect(ray)

        if t_left is None and t_right is None:
          return None
        elif t_left is None:
          return t_right
        elif t_right is None:
          return t_left
        else:
          return min(t_left, t_right)
    else:
      return None


class KDTree():
  DEPTH_BOUND = 8

  def __init__(self, mesh):
    self.root = self.branch(mesh.aabb, mesh.facets)

  def branch(self, aabb, facets, depth = 0) -> KDTreeNode:
    if len(facets) == 0: 
      return None

    if depth >= self.DEPTH_BOUND:
      # Return a leaf node
      return KDTreeNode(aabb, facets=facets)

    axis = depth % 3

    split_plane = aabb.center[axis]
    left, right = aabb.split(axis, split_plane)

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