import enum, math, traceback, json, os, glfw, sys
from PIL import Image

import numpy as np
from OpenGL.arrays import ArrayDatatype
from OpenGL.GL import *

from ctypes import c_void_p

from robot.common import Timer

from robot.spatial import vector3, Vector3, Matrix4, Dual, Quaternion, Transform

from .mech import serial

from robot.mech.robots import ABB_IRB_120

from .visual import Camera, STLParser, ShaderProgram
from .visual.exceptions import ParserError

from .visual import Buffer

camera = Camera(Vector3(0, -750, 350), Vector3(0, 0, 350), Vector3(0, 0, 1), 1)
theta = 0
use_link_colors = 0
pause = False

def on_resize(glfw_window, width, height):
  if width == 0 or height == 0:
    return

  glViewport(0, 0, width, height)
  camera.aspect = width / height

def scroll_callback(glfw_window, xoffset, yoffset):
  global theta

  forward = vector3.normalize(camera.position - camera.target)
  speed = 15
  if yoffset > 0:
    camera.position += speed * forward
  elif yoffset < 0:
    camera.position -= speed * forward

  if xoffset > 0:
    theta += 10
  elif xoffset < 0:
    theta -= 10

  forward = camera.position - camera.target
  radius = forward.length()

  x = radius * math.cos(math.radians(theta - 90))
  y = radius * math.sin(math.radians(theta - 90))

  camera.position = Vector3(x, y, 350)

def key_callback(window, key, scancode, action, mods):
  global theta
  global use_link_colors

  forward = camera.position - camera.target
  radius = forward.length()
  if key == glfw.KEY_RIGHT and (action == glfw.PRESS or action == glfw.REPEAT):
    theta += 10


    x = radius * math.cos(math.radians(theta - 90))
    y = radius * math.sin(math.radians(theta - 90))

    camera.position = Vector3(x, y, 350)

  elif key == glfw.KEY_LEFT and (action == glfw.PRESS or action == glfw.REPEAT):
    theta -= 10

    x = radius * math.cos(math.radians(theta - 90))
    y = radius * math.sin(math.radians(theta - 90))

    camera.position = Vector3(x, y, 350)

  elif key == glfw.KEY_C and action == glfw.PRESS:
    if use_link_colors == 0:
      use_link_colors = 1
    else:
      use_link_colors = 0

  elif key == glfw.KEY_SPACE and action == glfw.PRESS:
    global pause
    pause = not pause

def loadTexture():
  texture_im = Image.open('./robot/visual/res/grid.png')
  ix = texture_im.size[0]
  iy = texture_im.size[1]
  image = texture_im.tobytes("raw", "L", 0, -1)

  glEnable(GL_TEXTURE_2D)
  texid = glGenTextures(1)

  glBindTexture(GL_TEXTURE_2D, texid)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, ix, iy,
                0, GL_LUMINANCE, GL_UNSIGNED_BYTE, image)

  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

  return texid

if __name__ == "__main__":
  p = STLParser()

  filename = 'abb_irb_120.stl'
  meshes = []
  with Timer('Read meshes', False) as timer:
    try:
      meshes = p.parse(f'robot/mech/robots/meshes/{filename}')
    except ParserError as error:
      # print(traceback.format_exc())
      print('\033[91m' + f'Parsing error on line {error.line}: {error}' + '\033[0m')
      quit()

  robot_buffer = Buffer()

  robot_buffer.data_list = [([10000, 10000, 0,
                            0, 0, 1],
                            0),
                            ([-10000, 10000, 0,
                            0, 0, 1],
                            0),
                            ([-10000, -10000, 0,
                            0, 0, 1],
                            0),
                            ([-10000, -10000, 0,
                            0, 0, 1],
                            0),
                            ([10000, -10000, 0,
                            0, 0, 1],
                            0),
                            ([10000, 10000, 0,
                            0, 0, 1],
                            0)]

  robot_buffer.mesh_count = 1

  def robot_mesh_adapter(index, mesh, facet, vertex):
    float_data = [*vertex, *(facet.normal)]

    return (float_data, int(index))

  robot_buffer.append(meshes, robot_mesh_adapter)
  robot_data = robot_buffer.data()

  if not glfw.init():
    sys.exit('GLFW initialization failed')
    
  glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
  glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
  glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
  glfw.window_hint(glfw.SAMPLES, 4)
    
  window = glfw.create_window(900, 900, 'Robotpy', None, None)
    
  if not window:
    glfw.terminate()
    sys.exit('GLFW create window failed')

  glfw.make_context_current(window)

  glfw.set_window_size_callback(window, on_resize)
  glfw.set_key_callback(window, key_callback)
  glfw.set_scroll_callback(window, scroll_callback)

  glClearColor(0.65, 1.0, 0.50, 1)

  program = ShaderProgram('./robot/visual/glsl/vertex.glsl', './robot/visual/glsl/fragment.glsl')
  program.get_attributes()

  vao_id = glGenVertexArrays(1)
  glBindVertexArray(vao_id)

  vbo_id = glGenBuffers(1)

  glBindBuffer(GL_ARRAY_BUFFER, vbo_id)

  glBufferData(GL_ARRAY_BUFFER, robot_data.nbytes, robot_data, GL_STATIC_DRAW)

  glVertexAttribPointer(program.attribute_location('vin_position'), 3, GL_FLOAT, GL_FALSE, 28, None)
  glEnableVertexAttribArray(program.attribute_location('vin_position'))
  
  glVertexAttribPointer(program.attribute_location('vin_normal'), 3, GL_FLOAT, GL_FALSE, 28, c_void_p(12))
  glEnableVertexAttribArray(program.attribute_location('vin_normal'))

  glVertexAttribIPointer(program.attribute_location('vin_mesh_index'), 1, GL_INT, 28, c_void_p(24))
  glEnableVertexAttribArray(program.attribute_location('vin_mesh_index'))

  glBindBuffer(GL_ARRAY_BUFFER, 0)
  glBindVertexArray(0)

  glEnable(GL_DEPTH_TEST)
  glEnable(GL_MULTISAMPLE)
  glEnable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  link_colors = [
    (1, 0.25, 0.25),
    (0.5, 0.15, 0.85),
    (0.25, 0.25, 1),
    (0.5, 0.25, 1),
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1),
    (0.5, 1, 0.25)
  ]

  home_positions = ABB_IRB_120.poses([0] * 6)

  steps = -100 / 200
  value = 0

  while not glfw.window_should_close(window):
    with Timer('Frame Time', False) as timer:
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      
      new_positions = ABB_IRB_120.poses([math.radians(value)] * 6)

      if not pause:
        value += steps

        if value <= -100 or value >= 0:
          steps = -steps

      matrix_floats = []
      for home, new in zip(home_positions[1:], new_positions[1:]):
        matrix = Matrix4(new.transform)
        matrix_floats.extend(matrix.elements)

      model_matrices = np.array(matrix_floats, np.float32)

      glUseProgram(program.program_id)
      view_matrix = camera.camera_matrix().reshape(16, order='F')
      proj_matrix = camera.projection_matrix().reshape(16, order='F')
      try:
        program.uniforms['proj_matrix'].set_value(1, False, proj_matrix)
        program.uniforms['view_matrix'].set_value(1, False, view_matrix)
        program.uniforms['model_matrices'].set_value(6, False, model_matrices)

        program.uniforms['use_link_colors'].set_value(use_link_colors)
        program.uniforms['link_colors'].set_value(8, link_colors)
        program.uniforms['robot_color'].set_value(1, 0.5, 0, 0.5)
      except KeyError:
        pass

      glBindVertexArray(vao_id)

      glDrawArrays(GL_TRIANGLES, 0, robot_buffer.vertex_count())

      glUseProgram(0)
      glBindVertexArray(0)

      glfw.swap_buffers(window)
      # glFlush()

      glfw.poll_events()
