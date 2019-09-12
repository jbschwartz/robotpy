from typing import Union

from robot.mech                         import Link, Serial, Tool
from robot.spatial                      import Matrix4, Transform
from robot.visual                       import Camera, Renderer
from robot.visual.opengl.shader_program import ShaderProgram

def com(link: Link, sp: ShaderProgram, radius: float = 25.):
  sp.uniforms.radius   = radius
  sp.uniforms.position = link.properties.com

def triangle(camera: Camera, sp: ShaderProgram, scale: float = 1., opacity: float = 0.5, color = None):
  if not hasattr(camera, 'target'):
    return

  color = color or [0, 0.5, 1]

  # TODO: Hacky. See the TODO in Camera about the target attribute
  # Ultimately would like to see a vector passed (instead of camera)
  model = Matrix4([
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    camera.target.x, camera.target.y, camera.target.z, 1
  ])

  sp.uniforms.model_matrix = model
  sp.uniforms.scale_matrix = Matrix4([
    scale, 0, 0, 0,
    0, scale, 0, 0,
    0, 0, scale, 0,
    0, 0, 0, 1
  ])

  sp.uniforms.color_in   = color
  sp.uniforms.in_opacity = opacity

def trajectory(serial: Serial, sp: ShaderProgram, scale: float = 1., color = None):
  color = color or [1, 0, 0]

  sp.uniforms.model_matrix = serial.to_world

  sp.uniforms.scale_matrix = Matrix4([
    scale, 0, 0, 0,
    0, scale, 0, 0,
    0, 0, scale, 0,
    0, 0, 0, 1
  ])

  sp.uniforms.color_in   = color

def grid(placeholder, sp: ShaderProgram, scale: float = 1.):
  sp.uniforms.scale_matrix = Matrix4([
    scale, 0, 0, 0,
    0, scale, 0, 0,
    0, 0, scale, 0,
    0, 0, 0, 1
  ])

def bounding(tool, sp: ShaderProgram, color):
  sp.uniforms.model_matrix = Transform.from_axis_angle_translation(translation = tool.aabb.center)
  size = tool.aabb.size

  sp.uniforms.scale_matrix = Matrix4([
    size.x, 0, 0, 0,
    0, size.y, 0, 0,
    0, 0, size.z, 0,
    0, 0, 0, 1
  ])
  sp.uniforms.color_in = [0, 1, 1]
  sp.uniforms.in_opacity = 0.25

def tool(tool, sp: ShaderProgram):
  # TODO: This probably shouldn't be using the Serial shader.
  # It would be better to have a similar shader that handles individual objects
  # (instead of faking individual objects into "serial chains").
  sp.uniforms.model_matrices  = [tool.to_world] + [Transform()] * 6
  sp.uniforms.use_link_colors = False
  sp.uniforms.robot_color     = [0.5] * 3