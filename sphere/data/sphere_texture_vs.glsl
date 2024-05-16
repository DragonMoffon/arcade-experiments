#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform sampler2D elevText;


in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

out vec3 vs_normal;
out vec2 vs_uv;

void main(){
    mat4 mvp = window.projection * window.view;

    vec3 height = texture(elevText, in_uv).a * 8.849 * in_normal;
    gl_Position = mvp * vec4(in_position + height, 1.0);
    vs_normal = in_normal;
    vs_uv = in_uv;
}