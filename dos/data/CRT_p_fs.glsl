#version 330

//
// PUBLIC DOMAIN CRT STYLED SCAN-LINE SHADER
//
//   by Timothy Lottes
//
// This is more along the style of a really good CGA arcade monitor.
// With RGB inputs instead of NTSC.
//
// It is an example of what I personally would want as a display option for pixel art games.
// Please take and use, change, or whatever.
//
// Modified by DragonMoffon
//

const float hardScan = -8.0;  // Scanline hardness
const float hardPix = -6.0;  // hardness of scanlined pixels
const vec2 warp = vec2(1.0/32.0, 1.0/24.0);  // Display warp, should technically be circluar, but due to how the masking works that looks wrong.

// Amount of shadow mask to make the rgb pixel
const float maskDark=1.0;
const float maskLight=1.5;

//------------------------------------------------------------------------

uniform sampler2D source_texture;
uniform vec2 source_size;

in vec2 vs_uv;

out vec4 fs_colour;

//------------------------------------------------------------------------


// These methods may not be needed if using Linear textures and outputting in linear space for post-processing

// sRGB to Linear.
float ToLinear1(float c){return(c<=0.04045)?c/12.92:pow((c+0.055)/1.055,2.4);}
vec3 ToLinear(vec3 c){return vec3(ToLinear1(c.r),ToLinear1(c.g),ToLinear1(c.b));}

// Linear to sRGB.
float ToSrgb1(float c){return(c<0.0031308?c*12.92:1.055*pow(c,0.41666)-0.055);}
vec3 ToSrgb(vec3 c){return vec3(ToSrgb1(c.r),ToSrgb1(c.g),ToSrgb1(c.b));}


// Nearest emulated sample given floating point position and texel offset.
// Also zero's off screen.
vec4 Fetch(vec2 pos, vec2 off){
    pos = floor(pos*source_size+off) / source_size;
    if(max(abs(pos.x-0.5),abs(pos.y-0.5))>0.5) return vec4(0.0);
    return vec4(ToLinear(texture(source_texture, pos.xy).rgb), 1.0);
}

// Distance in emulated pixels to nearest texel.
vec2 Dist(vec2 pos){
    pos = pos * source_size / 12.0;
    return -(fract(pos)-vec2(0.5));
}
    
// 1D Gaussian.
float Gaus(float pos,float scale){
    return exp2(scale*pos*pos);
}

// 3-tap Gaussian filter along horz line.
vec4 Horz3(vec2 pos,float off){
    vec4 b=Fetch(pos,vec2(-1.0,off));
    vec4 c=Fetch(pos,vec2( 0.0,off));
    vec4 d=Fetch(pos,vec2( 1.0,off));
    float dst=Dist(pos).x;
    // Convert distance to weight.
    float wb=Gaus(dst-1.0,hardPix);
    float wc=Gaus(dst+0.0,hardPix);
    float wd=Gaus(dst+1.0,hardPix);
    // Return filtered sample.
    return (b*wb+c*wc+d*wd)/(wb+wc+wd);
}

// 5-tap Gaussian filter along horz line.
vec4 Horz5(vec2 pos,float off){
    vec4 a=Fetch(pos,vec2(-2.0,off));
    vec4 b=Fetch(pos,vec2(-1.0,off));
    vec4 c=Fetch(pos,vec2( 0.0,off));
    vec4 d=Fetch(pos,vec2( 1.0,off));
    vec4 e=Fetch(pos,vec2( 2.0,off));
    float dst=Dist(pos).x;
    // Convert distance to weight.
    float wa=Gaus(dst-2.0,hardPix);
    float wb=Gaus(dst-1.0,hardPix);
    float wc=Gaus(dst+0.0,hardPix);
    float wd=Gaus(dst+1.0,hardPix);
    float we=Gaus(dst+2.0,hardPix);
    // Return filtered sample.
    return (a*wa+b*wb+c*wc+d*wd+e*we)/(wa+wb+wc+wd+we);
}

// Return scanline weight.
float Scan(vec2 pos,float off){
    float dst=Dist(pos).y;
    return Gaus(dst+off,hardScan);
}

// Allow nearest three lines to effect pixel.
vec4 Tri(vec2 pos){
    vec4 a=Horz3(pos,-1.0);
    vec4 b=Horz5(pos, 0.0);
    vec4 c=Horz3(pos, 1.0);
    float wa=Scan(pos,-1.0);
    float wb=Scan(pos, 0.0);
    float wc=Scan(pos, 1.0);
    return vec4(a.rgb*wa + b.rgb*wb + c.rgb*wc, (a.a*wa + b.a*wb + c.a*wc) / (wa+wb+wc));
}

// Distortion of scanlines, and end of screen alpha.
vec2 Warp(vec2 pos){
    pos=pos*2.0-1.0;
    pos*=vec2(1.0+(pos.y*pos.y)*warp.x,1.0+(pos.x*pos.x)*warp.y);
    return pos*0.5+0.5;
}

// Shadow mask.
vec4 Mask(vec2 pos){
    pos.x += ceil(pos.y)*3.0;
    vec4 mask = vec4(vec3(maskDark), 1.0);
    pos.x = fract(pos.x/6.0);
    if (pos.x < 0.333) mask.r = maskLight;
    else if ( pos.x < 0.666) mask.g = maskLight;
    else mask.b = maskLight;
    return mask;
}    

void main(){
    vec2 pos = Warp(vs_uv);
    fs_colour = Tri(pos) * Mask(vs_uv * source_size);
    fs_colour.rgb = ToSrgb(fs_colour.rgb);
}