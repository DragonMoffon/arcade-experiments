#version 330

// https://learnopengl.com/Guest-Articles/2022/Phys.-Based-Bloom

// This shader performs downsampling on a texture,
// as taken from Call Of Duty method, presented at ACM Siggraph 2014.
// This particular method was customly designed to eliminate
// "pulsating artifacts and temporal stability issues".

// Remember to add bilinear minification filter for this texture!
// Remember to use a floating-point texture format (for HDR)!
// Remember to use edge clamping for this texture!
uniform sampler2D input;
uniform vec2 resolution;

in vec2 vs_uv;
out vec3 fs_colour;

void main(){
    float x = resolution.x;
    float y = resolution.y;

    // Take 13 samples around current texel:
    // a - b - c
    // - j - k -
    // d - e - f
    // - l - m -
    // g - h - i
    // === ('e' is the current texel) ===
    vec3 a = texture(input, vec2(vs_uv.x - 2*x, vs_uv.y + 2*y)).rgb;
    vec3 b = texture(input, vec2(vs_uv.x,       vs_uv.y + 2*y)).rgb;
    vec3 c = texture(input, vec2(vs_uv.x + 2*x, vs_uv.y + 2*y)).rgb;

    vec3 d = texture(input, vec2(vs_uv.x - 2*x, vs_uv.y)).rgb;
    vec3 e = texture(input, vec2(vs_uv.x,       vs_uv.y)).rgb;
    vec3 f = texture(input, vec2(vs_uv.x + 2*x, vs_uv.y)).rgb;
    
    vec3 g = texture(input, vec2(vs_uv.x - 2*x, vs_uv.y + 2*y)).rgb;
    vec3 h = texture(input, vec2(vs_uv.x,       vs_uv.y + 2*y)).rgb;
    vec3 i = texture(input, vec2(vs_uv.x + 2*x, vs_uv.y + 2*y)).rgb;
    
    vec3 j = texture(input, vec2(vs_uv.x - x, vs_uv.y + y)).rgb;
    vec3 k = texture(input, vec2(vs_uv.x + x, vs_uv.y + y)).rgb;
    vec3 l = texture(input, vec2(vs_uv.x - x, vs_uv.y - y)).rgb;
    vec3 m = texture(input, vec2(vs_uv.x + x, vs_uv.y - y)).rgb;

    fs_colour = max(vec3(0.0001), e*0.125 + (a+c+g+i)*0.03125 + (b+d+f+h)*0.0625 + (j+k+l+m)*0.125);
}