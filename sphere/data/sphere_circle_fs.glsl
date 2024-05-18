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
    vec3 primary = vec3(cos(a.x) * cos(a.y), sin(a.y), sin(a.x) * cos(a.y));
    vec3 secondary = vec3(cos(b.x) * cos(b.y), sin(b.y), sin(b.x) * cos(b.y));
    return acos(dot(primary, secondary));
}

float ring_error_sdf(vec4 ring, vec2 a){
    float d = angular_distance(a, ring.xy);
    float A = d - (1 + ring.w) * ring.z;
    float B = d - (1 - ring.w) * ring.z;

    return max(A, -B);
}


float ring_sdf(vec4 ring, vec2 a, float err){
    return abs(angular_distance(a, ring.xy) - (1 + err) * ring.z);
}

float point_sdf(vec2 p, vec2 a){
    return angular_distance(p, a);
}


void main(){
    float longitude = PI * (2.0 * -vs_uv.x - 1.0);
    float latitude = PI * (vs_uv.y - 0.5);
    vec2 coord = vec2(longitude, latitude);

    int overlap_count = 0;
    float closest_error = 100000000.0;
    float closest_line = 100000000.0;
    float closest_point = 10000000.0;
    for (int i = 0; i < rings.length(); i++){
        vec4 ring = rings[i];
        closest_point = min(closest_point, point_sdf(ring.xy, coord));
        float e_d = ring_error_sdf(ring, coord);
        if (e_d <= 0.0) overlap_count += 1;
        closest_line = min(closest_line, ring_sdf(ring, coord, 0.0));
        closest_error = min(min(ring_sdf(ring, coord, -ring.w), ring_sdf(ring, coord, ring.w)), closest_error);
    }

    vec4 base_colour = vec4(0.0);
    switch (overlap_count) {
        case 0:
            break;
        case 1:
            base_colour = vec4(1.0, 0.0, 0.0, 0.33);
            break;
        case 2:
            base_colour = vec4(1.0, 0.0, 0.0, 0.67);
            break;
        case 3:
            base_colour = vec4(1.0, 0.0, 0.0, 1.0);
    }


    if (closest_error <= line_width){
        float alpha = smoothstep(1.0, 0.0, closest_error / line_width);
        base_colour = base_colour + vec4(1.0, 0.0, 0.0, alpha);
    }
    if (closest_point <= line_width * 10.0){
        float alpha = smoothstep(1.0, 0.0, closest_point / (10.0 * line_width));
        base_colour = base_colour + vec4(1.0, 1.0, 1.0, alpha);
    }
    if (closest_line <= line_width){
        float t = closest_line / line_width;
        float alpha = smoothstep(1.0, 0.0, t);
        base_colour = vec4(0.0, 1.0, 0.0, alpha) * alpha + base_colour * (1.0 - alpha);
    }

    fs_colour = base_colour;
}
