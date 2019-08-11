in vec3 vout_color;
in vec3 vout_normal;
in vec3 frag_pos;

out vec4 fout_color;

layout (std140) uniform Light {
  vec3 position;
  vec3 color;
  float intensity;
};

void main(void)
{
  vec3 ambient = intensity * color;

  vec3 norm = normalize(vout_normal);
  vec3 lightDir = normalize(position - frag_pos);

  float diff = max(dot(norm, lightDir), 0.1);
  vec3 diffuse = diff * color;

  vec3 result = (ambient + diffuse) * vout_color;

  fout_color = vec4(result, 1.0);
}