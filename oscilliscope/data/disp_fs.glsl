#version 330

uniform sampler2D display_texture;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    fs_colour = vec4(texture(display_texture, vs_uv).rgb, 1.0);
}