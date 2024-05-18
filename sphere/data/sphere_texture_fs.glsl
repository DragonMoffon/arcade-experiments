#version 330

const float PI = 3.1415962;

uniform sampler2D wrldText;
uniform sampler2D elevText;

uniform vec3 light;

in vec2 vs_uv;
in vec3 vs_normal;

out vec4 fs_colour;

void main(){
    vec4 albedo = texture(wrldText, vs_uv);
    float longitude = PI * (2.0 * vs_uv.x - 1.0);

    vec3 forward = -vs_normal;
    vec3 right = vec3(-sin(longitude), 0.0, cos(longitude));
    vec3 up = cross(forward, right);

    vec3 norm = 2 * texture(elevText, vs_uv).rgb - 1;
    vec3 normal = right * norm.x + up * norm.y + forward * norm.z;
    float lighting = clamp(dot(normal, light) + 0.2, 0.0, 1.0);
    fs_colour = vec4(lighting * albedo.xyz, 1.0);
}