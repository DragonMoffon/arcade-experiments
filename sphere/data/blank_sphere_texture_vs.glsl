#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec3 in_position;
in vec2 in_uv;

out vec2 vs_uv;

void main(){
    mat4 mvp = window.projection * window.view;
    gl_Position = mvp * vec4(in_position, 1.0);
    vs_uv = in_uv;
}
