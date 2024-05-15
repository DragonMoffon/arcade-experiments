#version 330

uniform sampler2D wrldText;

in vec2 vs_uv;
in vec3 vs_normal;

out vec4 fs_colour;

void main(){
    fs_colour = texture(wrldText, vs_uv);
}