in vec3 vout_color;
in vec3 vout_normal;
in vec3 frag_pos;

out vec4 fout_color;

uniform vec3 light_position;
uniform vec3 light_color;
uniform float light_intensity;

void main(void)
{
  vec3 ambient = light_intensity * light_color;

  vec3 norm = normalize(vout_normal);
  vec3 lightDir = normalize(light_position - frag_pos);

  float diff = max(dot(norm, lightDir), 0.1);
  vec3 diffuse = diff * light_color;

  vec3 result = (ambient + diffuse) * vout_color;

  fout_color = vec4(result, 1.0);
}