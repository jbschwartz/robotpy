#if defined(VERTEX)
out vec2 mapping;

layout (std140) uniform Matrices
{
  mat4 projection;
  mat4 view;
};

// Ultimate position and radius (in camera space) of our drawn circle
uniform float radius;
uniform vec3  position;

// Create a square quad which is side length `radius` and centered at `position`
// Pass on a `mapping` to the fragment shader to determine fragment position with respect to center (i.e. `position`)
void main()
{
  vec2 offset;

  switch(gl_VertexID)
  {
  case 0: // Top-left
    mapping = vec2(-1.0, 1.0);  break;
  case 1: // Bottom-left
    mapping = vec2(-1.0, -1.0); break;
  case 2: // Top-right
    mapping = vec2(1.0, 1.0);   break;
  case 3: // Bottom-right
    mapping = vec2(1.0, -1.0);  break;
  }
  vec4 camera_corner_pos = view * vec4(position, 1.0);
  camera_corner_pos.xy += radius * mapping;

  gl_Position = projection * camera_corner_pos;
  gl_Position.z = -1;
}

#elif defined(FRAGMENT)

in vec2 mapping;

out vec4 fout_color;

// Shade the quad from the vertex shader into a circle with a black and white beachball pattern
void main()
{
  // I don't necessarily need to take the sqrt() performance hit but I prefer to work with radius instead of radius squared
  float radius = sqrt(dot(mapping, mapping));
  // This is how we generate our circle (by throwing out anything outside of the radius)
  if(radius > 1.0)
    discard;

  // Smooth the outside edge of the circle
  float alpha = 1 - smoothstep(0.95, 1.0, radius);
  // Smooth the black outline
  float color = 1 - smoothstep(0.85, 0.90, radius);

  // For the first and third quadrants of the circle, color the fill black (into a beachball)
  if (mapping.x * mapping.y > 0) color = 0;

  fout_color = vec4(color, color, color, alpha);
}

#endif