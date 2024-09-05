#version 330

uniform sampler2D display_texture;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    float gamma = 2.2;
    vec3 hdrcolour = texture(display_texture, vs_uv).rgb;

    vec3 mappedcolour = hdrcolour / (hdrcolour + vec3(1.0));

    vec3 gammacolour = pow(mappedcolour, vec3(1 / gamma));

    fs_colour = vec4(gammacolour, 1.0);
}