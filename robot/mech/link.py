from robot.spatial.frame import Frame

class Link:
  def __init__(self, name, color, mesh_file):
    # TODO: Mass, COM, Moments of Inertia
    self.frame = Frame()
    self.name = name
    self.color = color
    self.mesh_file = mesh_file