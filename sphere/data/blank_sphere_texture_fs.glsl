#version 330

uniform sampler2D texture0;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    fs_colour = texture(texture0, vs_uv);
}
