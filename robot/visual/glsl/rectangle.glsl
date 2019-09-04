#if defined(VERTEX)

in vec3 vin_position;

uniform mat4 scale_matrix;
uniform vec3 position;

const mat4 view_2d = mat4(vec4( 2,  0,  0,  0),
                          vec4( 0, -2,  0,  0),
                          vec4( 0,  0,  1,  0),
                          vec4(-1,  1,  0,  1));

void main()
{
  gl_Position = view_2d * (scale_matrix * vec4(vin_position, 1.0) + vec4(position, 0.0));
}

#elif defined(FRAGMENT)

out vec4 gl_FragColor;

uniform vec3 color;

void main(void)
{
  gl_FragColor = vec4(color, 1);
}

#endif