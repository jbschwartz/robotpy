#if defined(VERTEX)

in vec2 vin_position;
in vec2 vin_texCoords;

out vec2 texCoords;

uniform mat4 scale_matrix;
uniform vec3 position;

const mat4 view_2d = mat4(vec4( 2,  0,  0,  0),
                          vec4( 0, -2,  0,  0),
                          vec4( 0,  0,  1,  0),
                          vec4(-1,  1,  0,  1));

void main()
{
  gl_Position = view_2d * (scale_matrix * vec4(vin_position, 0, 1.0) + vec4(position, 0.0));
  texCoords = vec2(vin_texCoords);
}

#elif defined(FRAGMENT)

out vec4 gl_FragColor;
in vec2 texCoords;
uniform sampler2D texture1;
uniform vec3 color;

void main(void)
{
  vec4 alpha = texture(texture1, texCoords);
  gl_FragColor = vec4(color, alpha.r);
}

#endif