#version 330

in vec3 vin_position;

uniform mat4 proj_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

void main()
{
  gl_Position = proj_matrix * view_matrix * model_matrix * vec4(vin_position, 1.0);
}