#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec2 in_pos;
in vec4 in_colour;

out vec4 vs_colour;

void main() {
    gl_Position = window.projection * window.view * vec4(in_pos, 0.0, 1.0);

    vs_colour = in_colour;
}