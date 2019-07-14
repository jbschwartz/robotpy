#version 330

out vec4 fout_color;

uniform vec3 color_in;
uniform float in_opacity;

void main(void)
{
  fout_color = vec4(color_in, in_opacity);
}