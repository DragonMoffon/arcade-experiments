#version 330

uniform sampler2D output_texture;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    fs_colour = texture(output_texture, vs_uv);
}