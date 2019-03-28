#version 330

in vec3 vout_color;
in vec3 vout_normal;
in vec3 frag_pos;

out vec4 fout_color;

void main(void)
{
  vec3 lightPos = vec3(400, -400, 1200);
  vec3 lightColor = vec3(1, 1, 1);

  float ambientStrength = 0.3;
  vec3 ambient = ambientStrength * lightColor;

  vec3 norm = normalize(vout_normal);
  vec3 lightDir = normalize(lightPos - frag_pos); 

  float diff = max(dot(norm, lightDir), 0.1);
  vec3 diffuse = diff * lightColor;

  vec3 color = vout_color;

  // if (vout_usecoords == 1) {
  //   vec4 tex_color = texture(ourTexture, texcoords);
  //   if (tex_color.a < 1) {
  //     color = vec3(1,1,1); 
  //   } else {
  //     color = vec3(0.55, 0.25, 0.95);//tex_color.xyz; 
  //   }
  // }
  
  vec3 result = (ambient + diffuse) * color;


  fout_color = vec4(result, 1.0);
}