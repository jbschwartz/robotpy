from robot.spatial.vector3   import Vector3
from robot.spatial.ray       import Ray
from robot.visual.exceptions import DegenerateTriangleError

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
        closest = None

        for triangle in self.facets:
          t = triangle.intersect(ray)
          if t and (closest is None or t < closest):
            closest = t

        return closest
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
  MINIMUM_FACETS = 20
  DEPTH_BOUND = 3

  def __init__(self, mesh):
    self.mesh = mesh

    self.root = self.branch(mesh.aabb, mesh.facets)

  def branch(self, aabb, facets, depth = 0) -> KDTreeNode:
    num_facets = len(facets)

    if num_facets == 0: 
      return None

    # TODO: Is this a good condition to stop branching?
    if num_facets <= self.MINIMUM_FACETS or depth >= self.DEPTH_BOUND:
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