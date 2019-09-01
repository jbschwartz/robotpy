from .intersection import Intersection
from .ray          import Ray

DEPTH_BOUND = 8

class KDTreeNode():
  def __init__(self, aabb, facets):
    self.aabb = aabb
    self.facets = facets
    self.children = []

  def is_leaf(self):
    '''Return True if the KDTreeNode is a leaf node.'''
    return len(self.children) == 0

  def can_branch(self, depth):
    '''Return True if the KDTreeNode can be split into two child branches.'''
    # TODO: Maybe use a more sophisticated cost function to evaluate whether we should branch
    return len(self.facets) > 0 and depth < DEPTH_BOUND

  def splitting_plane(self, depth):
    '''Get the splitting plane (i.e. axis and value) for the given depth.'''
    # TODO: Maybe use a more sophisticated splitting plane generation like SAH.
    axis = depth % 3
    plane_value = self.aabb.center[axis]

    return axis, plane_value

  def split_facets(self, axis, plane_value):
    '''Split the list of facets in the node into left and right lists based on splitting plane.'''
    left, right = [], []

    for facet in self.facets:
      # Check minimum bound on left and maximum bound on right so that the triangle is not included in any list twice
      # This covers both scenarios: facets belonging to one side only or both sides
      if facet.aabb.min[axis] < plane_value:
        left.append(facet)
      if facet.aabb.max[axis] > plane_value:
        right.append(facet)

    return left, right

  def candidate_children(self, splitting_plane):
    '''Get child AABBs and facet lists from a given splitting plane.'''
    child_boxes = self.aabb.split(*splitting_plane)
    child_facets = self.split_facets(*splitting_plane)

    return zip(child_boxes, child_facets)

  def branch(self, depth = 0):
    '''If possible, split the current KDTreeNode into two children nodes.'''
    if not self.can_branch(depth):
      return

    splitting_plane = self.splitting_plane(depth)

    for child in self.candidate_children(splitting_plane):
      node = KDTreeNode(*child)
      node.branch(depth + 1)

      self.children.append(node)

    # Interrior nodes to the KDTree should not have any facets (only leaf nodes should).
    # If we've gotten this far, this node is an interrior node
    self.facets = None

  def intersect(self, ray: Ray) -> Intersection:
    """Intersect ray with node and return closest found intersection. Return Intersection.Miss() for no intersections."""
    if not self.aabb.intersect(ray):
      return Intersection.Miss()

    if self.is_leaf():
      return ray.closest_intersection(self.facets)
    else:
      return ray.closest_intersection(self.children)

class KDTree():
  def __init__(self, mesh):
    self.root = KDTreeNode(mesh.aabb, mesh.facets)

    self.construct()

  def construct(self):
    self.root.branch()

  def intersect(self, ray: Ray) -> Intersection:
    return self.root.intersect(ray)

  def update(self, mesh, facet):
    # The full tree needs to be reconstructed when the mesh is changed so just re-initialize
    self.__init__(mesh)