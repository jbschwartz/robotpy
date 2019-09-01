#if defined(VERTEX)

in vec3 vin_position;

layout (std140) uniform Matrices
{
  mat4 projection;
  mat4 view;
};

uniform mat4 scale_matrix;
uniform vec3 top_left;

void main()
{
  gl_Position = scale_matrix * vec4(vin_position, 1.0) + vec4(top_left, 0.0);
}

#elif defined(FRAGMENT)

out vec4 gl_FragColor;

void main(void)
{
  gl_FragColor = vec4(1, 0, 0, 1);
}

#endif