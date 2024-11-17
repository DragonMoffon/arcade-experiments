#version 330
// https://github.com/s-ilent/custom-tonemap/blob/main/Runtime/Shaders/AgxTonemapper.hlsl

// https://iolite-engine.com/blog_posts/minimal_agx_implementation
//
// MIT License
//
// Copyright (c) 2024 Missing Deadlines (Benjamin Wrensch)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// Values used to derive this implementation are sourced from Troy’s initial AgX implementation/OCIO config file available here:
//   https://github.com/sobotka/AgX

// AgX Tone Mapping implementation based on Three.js,
// which is based on Filament's, which in turn is based
// on Blender's implementation using rec 2020 primaries
// https://github.com/mrdoob/three.js/pull/27366
// https://github.com/google/filament/pull/7236
// Inputs and outputs are encoded as Linear-sRGB.

#define FLT_EPSILON 1.192092896e-07
#define FLT_MIN     1.175494351e-38
#define FLT_MAX     3.402823466e+38

// LOG2_MIN      = -10.0
// LOG2_MAX      =  +6.5
// MIDDLE_GRAY   =  0.18
const float AgxMinEv = - 12.47393;  // log2( pow( 2, LOG2_MIN ) * MIDDLE_GRAY )
const float AgxMaxEv = 4.026069;    // log2( pow( 2, LOG2_MAX ) * MIDDLE_GRAY )
const float AgxDiffEv = AgxMaxEv - AgxMinEv;

const mat3 linear_rec2020_to_linear_srgb = mat3(
    1.6605, -0.5876, -0.0728,
    -0.1246, 1.1329, -0.0083,
    -0.0182, -0.1006, 1.1187
);
const mat3 linear_srgb_to_linear_rec2020 = mat3(
    0.6274, 0.3293, 0.0433,
    0.0691, 0.9195, 0.0113,
    -0.0182, -0.1006, 1.1187
);
const mat3 AGX_inset = mat3(
    0.85662717, 0.09512124, 0.048251607,
    0.13731897, 0.761242, 0.10143904,
    0.11189821, 0.076799415, 0.81130236
);
const mat3 AGX_outset = mat3(
    1.1271006, -0.11060664, -0.016493939,
    -0.14132977, 1.1578237, -0.016493939,
    -0.14132977, -0.11060664, 1.2519364
);
const vec3 lw = vec3(0.2126, 0.7152, 0.0722);

// Mean error^2: 3.6705141e-06
vec3 approximate_agx_contrast(vec3 x){
    vec3 x2 = x * x;
    vec3 x4 = x2 * x2;
    vec3 x6 = x4 * x2;
    return - 17.86    * x6 * x
           + 78.01    * x6
           - 126.7    * x4 * x
           + 92.06    * x4
           - 28.72    * x2 * x
           + 4.361    * x2
           - 0.1718   * x
           + 0.002857;
}

vec3 agx(vec3 col){
    // col = linear_srgb_to_linear_rec2020 * col;
    col = AGX_inset * col;
    col = clamp(log2(col), AgxMinEv, AgxMaxEv);
    col = (col - AgxMinEv) / AgxDiffEv;
    return approximate_agx_contrast(col);
}

vec3 agx_transfer_function(vec3 col){
    col = AGX_outset * col;
    col = max(vec3(0.0), col);
    col = pow(col, vec3(2.2));
    // col = linear_rec2020_to_linear_srgb * col;

    return col;
}

uniform vec3 offset;
uniform vec3 slope;
uniform vec3 power;
uniform float saturation;

vec3 agx_look(vec3 col){
    float luma = dot(col, lw);

    col = pow(col * slope + offset, power);
    return luma + saturation * (col - luma);
}

uniform sampler2D source;

in vec2 vs_uv;

out vec4 fs_colour;

void main(){
    vec4 source_colour = texture(source, vs_uv);
    vec3 col = agx(source_colour.rgb);
    col = agx_look(col);
    // col = agx_transfer_function(col);
    fs_colour = vec4(col, 1.0);
}