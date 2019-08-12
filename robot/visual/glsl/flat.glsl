#if defined(VERTEX)

in vec3 vin_position;

layout (std140) uniform Matrices
{
  mat4 projection;
  mat4 view;
};

uniform mat4 model_matrix;
uniform mat4 scale_matrix;

void main()
{
  gl_Position = projection * view * model_matrix * scale_matrix * vec4(vin_position, 1.0);
}

#elif defined(FRAGMENT)

out vec4 fout_color;

uniform vec3 color_in;
uniform float in_opacity;

void main(void)
{
  fout_color = vec4(color_in, in_opacity);
}

#endif