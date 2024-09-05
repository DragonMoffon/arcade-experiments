#version 330

uniform float radius;
uniform float decay;
uniform vec4 signal;

uniform sampler2D display_texture;

in vec2 vs_pos;
in vec2 vs_uv;

out vec4 fs_colour;

float gaussian(vec2 src, vec2 pnt){
    vec2 diff = pnt - src;
    return signal.z * radius / dot(diff, diff);
}

float signal_decay(float s){
    return s * exp(-decay * signal.a);
}

void main(){
    vec3 colour = texture(display_texture, vs_uv).rgb;
    colour = vec3(signal_decay(colour.r), signal_decay(colour.g), signal_decay(colour.b));
    float str = gaussian(signal.xy, vs_pos);
    colour += vec3(str);
    fs_colour = vec4(colour, 1.0);
}