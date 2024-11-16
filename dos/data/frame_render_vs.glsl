#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;


in vec2 in_vert;
in vec2 in_uv;

out vec2 vs_uv;

void main(){
    gl_Position = window.projection * window.view * vec4(in_vert, 0.0, 1.0);
    vs_uv = in_uv;
}