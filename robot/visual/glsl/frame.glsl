#if defined(VERTEX)
in vec3 vin_position;
in vec3 vin_normal;

out vec3 vout_color;
out vec3 vout_normal;
out vec3 frag_pos;

layout (std140) uniform Matrices
{
  mat4 projection;
  mat4 view;
};

uniform mat4 model_matrix;
uniform mat4 scale_matrix;

void main()
{
  vec2 offset;

  if(gl_VertexID < 36) {
    vout_color = vec3(0.5, 0, 0);
  } else if(gl_VertexID < 72) {
    vout_color = vec3(0, 0.5, 0);
  } else if(gl_VertexID < 108) {
    vout_color = vec3(0, 0, 0.5);
  } else {
    vout_color = vec3(1, 1, 0);
  }

  vout_normal = vec3(model_matrix * vec4(vin_normal, 0));
  frag_pos =  vec3(model_matrix * vec4(vin_position, 1));
  gl_Position = projection * view * model_matrix * scale_matrix * vec4(vin_position, 1.0);
}

#elif defined(FRAGMENT)

in vec3 vout_color;
in vec3 vout_normal;
in vec3 frag_pos;

out vec4 fout_color;

layout (std140) uniform Light {
  vec3 position;
  vec3 color;
  float intensity;
};

void main()
{
  vec3 ambient = intensity * color;

  vec3 norm = normalize(vout_normal);
  vec3 lightDir = normalize(position - frag_pos);

  float diff = max(dot(norm, lightDir), 0.1);
  vec3 diffuse = diff * color;

  vec3 result = (ambient + diffuse) * vout_color;

  fout_color = vec4(result, 1.0);
}

#endif