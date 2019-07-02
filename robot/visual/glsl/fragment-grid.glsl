#version 330

in vec4 vout_world_pos;
out vec4 gl_FragColor;

uniform float step_size;
uniform float minor_step_size;
uniform vec3 in_grid_color; 
uniform vec3 in_minor_grid_color; 

void main(void)
{
  vec2 major_f = fract(vout_world_pos.xy / step_size);
  vec2 minor_f = fract(vout_world_pos.xy / minor_step_size);

  vec4 background = vec4(0, 0, 0, 0);
  vec4 grid_color = vec4(in_grid_color, 1);
  vec4 minor_grid_color = vec4(in_minor_grid_color, 1);

  float line_width = 0.025;
  vec2 major_mult = smoothstep(0, line_width, major_f) - smoothstep(1 - line_width, 1, major_f);
  vec2 minor_mult = smoothstep(0, line_width, minor_f) - smoothstep(1 - line_width, 1, minor_f);

  float radius = sqrt(vout_world_pos.x * vout_world_pos.x + vout_world_pos.y * vout_world_pos.y);
  // float alpha = 1

  float major_blend = min(major_mult.x, major_mult.y);
  vec4 major_color = mix(grid_color, background, major_blend);
  vec4 minor_color = mix(minor_grid_color, background, min(minor_mult.x, minor_mult.y));

  // float blend = smoothstep(0, 0, major_blend);

  vec4 total = major_color + minor_color;
  total.a = total.a - smoothstep(750, 2500, radius);

  gl_FragColor = total; //+ major_color;
  // gl_FragColor.a = gl_;
}