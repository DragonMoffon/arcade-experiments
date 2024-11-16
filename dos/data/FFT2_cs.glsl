#version 330
#extension GL_ARB_compute_shader : require

layout (local_size_x = 1, local_size_y = 1, local_size_z) in;

void FFT(int N, int R, int Ns, vec2 dataT, vec2 dataO){
    int j = 
}