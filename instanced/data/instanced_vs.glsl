#version 330 core

struct Star {
    vec2 pos;
    float angle;
    float scale;
};

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform StarBlock {
    Star[1024] data;
} stars;

in vec2 in_pos;
in vec3 in_colour;

out vec3 vs_colour;

void main(){
    Star data = stars.data[gl_InstanceID];

    float c = cos(data.angle), s = sin(data.angle);
    vec2 pos = data.scale * vec2(c * in_pos.x - s * in_pos.y, s * in_pos.x + c * in_pos.y) + data.pos;
    gl_Position = window.projection * window.view * vec4(pos, -data.scale / 1000.0, 1.0);

    vs_colour = in_colour;
}