in vec3 vin_position;
in vec3 vin_normal;
in int vin_mesh_index;

out vec3 vout_color;
out vec3 vout_normal;
out vec3 frag_pos;

layout (std140) uniform Matrices
{
  mat4 projection;
  mat4 view;
};

uniform mat4 model_matrices[7];

uniform bool use_link_colors;
uniform vec3 link_colors[7];
uniform vec3 robot_color;

void main(void)
{
  if(use_link_colors) {
    vout_color = link_colors[vin_mesh_index];
  } else {
    vout_color = robot_color;
  }

  mat4 model_matrix = model_matrices[vin_mesh_index];

  vout_normal = vec3(model_matrix * vec4(vin_normal, 0));
  frag_pos =  vec3(model_matrix * vec4(vin_position, 1));
  gl_Position = projection * view * model_matrix * vec4(vin_position, 1.0);
}