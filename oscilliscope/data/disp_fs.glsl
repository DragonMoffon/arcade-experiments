#version 330

uniform sampler2D display_texture;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    float gamma = 1.0;
    fs_colour = vec4(pow(texture(display_texture, vs_uv).rgb, vec3(1.0/gamma)), 1.0);
}