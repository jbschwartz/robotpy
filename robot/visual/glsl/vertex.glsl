#version 330

in vec3 vin_position;
in vec3 vin_normal;
in int vin_mesh_index;
// in int gl_VertexID;

out vec3 vout_color;
out vec3 vout_normal;
out vec3 frag_pos;

uniform mat4 proj_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrices[6];

// uniform int link_end_indices[8];
uniform bool use_link_colors;
uniform vec3 link_colors[8];
uniform vec3 robot_color;

// int vin_mesh_index(in int vertex_id);

void main(void)
{
  // int vin_mesh_index = vin_mesh_index(gl_VertexID);

  // int index = int(vin_mesh_index);
  if(use_link_colors) {
    vout_color = link_colors[vin_mesh_index];
  } else {
    vout_color = robot_color;
  }

  mat4 model_matrix = (vin_mesh_index > 1) ? model_matrices[vin_mesh_index - 2] : mat4(1.0);

  vout_normal = vec3(model_matrix * vec4(vin_normal, 0));
  frag_pos =  vec3(model_matrix * vec4(vin_position, 1));
  gl_Position = proj_matrix * view_matrix * model_matrix * vec4(vin_position, 1.0);
  // gl_Position = proj_matrix * view_matrix * vec4(vin_position, 1.0);
}

// int vin_mesh_index(in int vertex_id) {
//   for(int i = 0; i < link_end_indices.length(); ++i) {
//     if(vertex_id < link_end_indices[i]) {
//       return i;
//     }
//   }

//   return -1;
// }