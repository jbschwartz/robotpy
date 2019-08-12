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
  mat4 new_mv = view * model_matrix;

  new_mv[0][0] = 1.0;
  new_mv[0][1] = 0.0;
  new_mv[0][2] = 0.0;

  new_mv[1][0] = 0.0;
  new_mv[1][1] = 1.0;
  new_mv[1][2] = 0.0;

  new_mv[2][0] = 0.0;
  new_mv[2][1] = 0.0;
  new_mv[2][2] = 1.0;

  gl_Position = projection * new_mv * scale_matrix * vec4(vin_position, 1.0);
  gl_Position.z = -1;
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