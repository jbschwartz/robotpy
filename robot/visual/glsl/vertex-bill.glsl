#version 330

in vec3 vin_position;

uniform mat4 proj_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;
uniform mat4 scale_matrix;

void main()
{
  mat4 new_mv = view_matrix * model_matrix;

  new_mv[0][0] = 1.0; 
  new_mv[0][1] = 0.0; 
  new_mv[0][2] = 0.0; 

  new_mv[1][0] = 0.0; 
  new_mv[1][1] = 1.0; 
  new_mv[1][2] = 0.0; 

  new_mv[2][0] = 0.0; 
  new_mv[2][1] = 0.0; 
  new_mv[2][2] = 1.0; 

  gl_Position = proj_matrix * new_mv * scale_matrix * vec4(vin_position, 1.0);
  gl_Position.z = -1;
}