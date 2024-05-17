#version 430

const float PI = 3.1415962;

uniform float line_width;
uniform float error_transparency;

// A ring is composed of: long, lat, radius, error
layout (binding = 0) buffer Rings
{
    vec4 rings[];
};

in vec2 vs_uv;

out vec4 fs_colour;


float angular_distance(vec2 a, vec2 b){
    return acos( sin(a.x) * sin(b.x) + cos(a.x) * cos(b.x) * cos(a.y - b.y));
}

float ring_error_sdf(vec4 ring, vec2 a){
    float d = angular_distance(a, ring.xy);
    float A = d - (1 + ring.w) * ring.z;
    float B = d - (1 - ring.w) * ring.z;

    return max(A, -B);
}


float ring_sdf(vec4 ring, vec2 a){
    return angular_distance(a, ring.xy);
}


void main(){
    float longitude = -PI + 2.0 * PI * vs_uv.x;
    float latitude = -PI / 2.0 + PI * vs_uv.y;
    vec2 coord = vec2(longitude, latitude);

    float error = 0.0;
    bool is_on_line = false;
    for (int i = 0; i < 1; i++){
        vec4 ring = rings[i];
        float e_d = ring_error_sdf(ring, coord);
        if (e_d <= 0.0) error += error_transparency;
        float m_d = ring_sdf(ring, coord);
        if (m_d <= line_width) is_on_line = true;
    }

    fs_colour = is_on_line ? vec4(1.0, 1.0, 1.0, 1.0) : vec4(vs_uv, 0.5, error);
}
