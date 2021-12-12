#if defined(VERTEX)

in vec3 vin_position;
out vec4 vout_world_pos;
out vec4 gl_Position;

layout (std140) uniform Matrices
{
  mat4 projection;
  mat4 view;
};

uniform mat4 scale_matrix;

void main()
{
  vout_world_pos = scale_matrix * vec4(vin_position, 1.0);
  gl_Position = projection * view * vout_world_pos;
}

#elif defined(FRAGMENT)

in vec4 vout_world_pos;

uniform float step_size;
uniform float minor_step_size;
uniform vec3 in_grid_color;
uniform vec3 in_minor_grid_color;

void main(void)
{
  // Pick a coordinate to visualize in a grid
  vec2 coord = vout_world_pos.xy / 500;
  vec2 coord2 = vout_world_pos.xy / 100;

  // Compute anti-aliased world-space grid lines
  vec2 line = abs(fract(coord) - 0.5) / fwidth(coord);
  vec2 line2 = abs(fract(coord2) - 0.5) / fwidth(coord2);
  vec2 weight = max(vec2(0), min(line - 0.35, vec2(1)));
  vec2 weight2 = max(vec2(0), min(line2 - 0.005, vec2(1)));

  vec4 background = vec4(0, 0, 0, 0);
  vec4 grid_color = vec4(0.55, 0.55, 0.55, 1);
  vec4 minor_grid_color = vec4(0.95, 0.95, 0.95, 1);

  // Just visualize the grid lines directly
  float major_blend = min(weight.x, weight.y);
  float minor_blend = min(weight2.x, weight2.y);
  vec4 major_color = mix(grid_color, background, major_blend);
  vec4 minor_color = mix(minor_grid_color, background, minor_blend);

  vec4 total;
  if (major_blend != 1) {
    total = major_color;
  } else{
    total = minor_color;
  }

  gl_FragColor = total;
  gl_FragColor.a = gl_FragColor.a - smoothstep(2000, 4000, length(vout_world_pos.xy));

}

#endif