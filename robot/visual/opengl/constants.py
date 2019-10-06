import numpy     as np
import OpenGL.GL as gl

# Map numpy types to OpenGL types
TYPE_NUMPY_TO_GL = {
  np.dtype('int8').base:    gl.GL_BYTE,
  np.dtype('int16').base:   gl.GL_SHORT,
  np.dtype('int32').base:   gl.GL_INT,
  np.dtype('uint8').base:   gl.GL_UNSIGNED_BYTE,
  np.dtype('uint16').base:  gl.GL_UNSIGNED_SHORT,
  np.dtype('uint32').base:  gl.GL_UNSIGNED_INT,

  np.dtype('float16').base: gl.GL_HALF_FLOAT,
  np.dtype('float32').base: gl.GL_FLOAT,
  np.dtype('float64').base: gl.GL_DOUBLE
}

# A subset of OpenGL integer types used in this module
GL_INTEGER_TYPES = [
  gl.GL_BYTE,
  gl.GL_SHORT,
  gl.GL_INT,
  gl.GL_UNSIGNED_BYTE,
  gl.GL_UNSIGNED_SHORT,
  gl.GL_UNSIGNED_INT
]

# A subset of OpenGL floating point types used in this module
GL_FLOAT_TYPES = [
  gl.GL_HALF_FLOAT,
  gl.GL_FLOAT,
  gl.GL_DOUBLE
]