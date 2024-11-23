#version 330

uniform sampler2D output_texture;
const vec2 warp = vec2(1.0/32.0, 1.0/24.0);  // Display warp, should technically be circluar, but due to how the masking works that looks wrong.

in vec2 vs_uv;

out vec4 fs_colour;

vec2 Warp(vec2 pos){
    pos=pos*2.0-1.0;
    pos*=vec2(1.0+(pos.y*pos.y)*warp.x,1.0+(pos.x*pos.x)*warp.y);
    return pos*0.5+0.5;
}

void main(){
    vec2 pos = Warp(vs_uv);
    if(max(abs(pos.x-0.5),abs(pos.y-0.5))>0.5) discard;
    fs_colour = texture(output_texture, pos);
}