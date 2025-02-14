#version 330 core

in vec3 vs_colour;

out vec4 fs_colour;

void main(){
    fs_colour = vec4(vs_colour, 1.0);
}