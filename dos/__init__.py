from common.data_loading import make_package_path_finder
import dos.data as data

get_image_path = make_package_path_finder(data, 'png')
get_shader_path = make_package_path_finder(data, 'glsl')