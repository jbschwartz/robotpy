#version 330

out vec4 fout_color;

uniform vec3 color_in;

void main(void)
{
  fout_color = vec4(color_in, 1.0);
}