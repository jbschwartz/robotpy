import json, math

import OpenGL.GL as gl

from robot.common          import Bindings, Timer
from robot.mech            import Serial, Simulation
from robot.mech            import tool
from robot.spatial.euler   import Axes, Order
from robot.spatial         import Matrix4, Mesh, Transform, Quaternion, Vector3
from robot.traj.linear_os  import LinearOS
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.opengl.buffer            import Buffer
from robot.visual.opengl.shader_program    import ShaderProgram
from robot.visual.opengl.uniform_buffer    import Mapping, UniformBuffer

import robot.instance_functions as pif

import robot.visual as vis

def setup():
  with Timer('Initialize Window') as t:
    window = vis.Window(750, 750, "robotpy")

  sim = Simulation()

  grid_buffer = Buffer.from_points([
    Vector3( 0.5,  0.5,  0,),
    Vector3(-0.5,  0.5,  0,),
    Vector3(-0.5, -0.5,  0,),
    Vector3(-0.5, -0.5,  0,),
    Vector3( 0.5, -0.5,  0,),
    Vector3( 0.5,  0.5,  0,)
  ])

  camera = vis.Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1))
  light = vis.AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)
  renderer = vis.Renderer(camera, light)

  renderer.register_entity_type(
    name         = 'grid',
    buffer       = grid_buffer,
    per_instance = pif.grid
  )

  renderer.add('grid', None, None, scale=10000)

  renderer.add('trajectory', serials[0], None)

  bindings = Bindings()
  settings = vis.CameraSettings()
  camera_controller = vis.CameraController(camera, settings, bindings, sim, window)

  matrix_ub = UniformBuffer("Matrices", 1)

  matrix_ub.bind(Mapping(
    camera, ['projection.matrix', 'world_to_camera']
  ))

  light_ub = UniformBuffer("Light", 2)

  light_ub.bind(Mapping(
    light, ['position', 'color', 'intensity']
  ))

  renderer.ubos = [matrix_ub, light_ub]

  return window, renderer

from robot.visual.gui import Rectangle

if __name__ == "__main__":
  window, renderer = setup()

  rectangles = [
    Rectangle(Vector3(0.125, 0.375), 0.125, 0.125, color=[0.25] * 3),
    Rectangle(Vector3(0, 0.5), 0.25, 0.25, color=[0.65] * 3)
  ]

  rectangle_buffer = Buffer.from_points([
    Vector3( 2,  0,  0),
    Vector3( 0,  0,  0),
    Vector3( 0, -2,  0),
    Vector3( 0, -2,  0),
    Vector3( 2, -2,  0),
    Vector3( 2,  0,  0)
  ])

  def rectangle_instance(rectangle: Rectangle, sp: ShaderProgram):
    gl.glDisable(gl.GL_DEPTH_TEST)

    sp.uniforms.color        = rectangle.color
    sp.uniforms.top_left     = rectangle.position
    sp.uniforms.scale_matrix = Matrix4.from_scale(Vector3(rectangle.width, rectangle.height, 1))

  renderer.register_entity_type(
    name         = 'rectangle',
    buffer       = rectangle_buffer,
    per_instance = rectangle_instance
  )

  renderer.add_many('rectangle', rectangles, None)

  window.run(fps_limit = 60)