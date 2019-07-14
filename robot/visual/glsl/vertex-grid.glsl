in vec3 vin_position;
out vec4 vout_world_pos;
out vec4 gl_Position;

uniform mat4 proj_matrix;
uniform mat4 view_matrix;
uniform mat4 scale_matrix;

void main()
{
  vout_world_pos = scale_matrix * vec4(vin_position, 1.0);
  gl_Position = proj_matrix * view_matrix * vout_world_pos;
}