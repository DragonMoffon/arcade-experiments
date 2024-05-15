#version 330

uniform sampler2D wrldText;

in vec2 vs_uv;
in vec3 vs_normal;

out vec4 fs_colour;

void main(){
    vec4 albedo = texture(wrldText, vs_uv);
    float lighting = min(1.0, dot(vs_normal, vec3(1.0, 0.0, 0.0)) + 0.5);
    fs_colour = vec4(lighting * albedo.xyz, 1.0);
}