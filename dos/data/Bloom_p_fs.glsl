#version 330

uniform sampler2D source;
uniform sampler2D blur;
uniform float strength;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    fs_colour = vec4(mix(texture(source, vs_uv).rgb, texture(blur, vs_uv).rgb, strength), 1.0);
}