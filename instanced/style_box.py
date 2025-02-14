from math import tau, cos, sin

from arcade import Vec2
from arcade.types import RGBA255

QUARTER_ARC_RADIANS = tau / 4.0

def gen_stylebox(
        width: float,
        height: float,
        position: Vec2,
        corner_radii: tuple[float, float, float, float],
        border_thickness: tuple[float, float, float, float],
        inner_colour: RGBA255 = (255, 255, 255, 255),
        border_colour: RGBA255 = (255, 255, 255, 255),
        gradient: bool = False,
        *,
        resolution: int = 12,
        inner_corner_radius_control: bool = False
):
    if all( b <= 0.0 for b in border_thickness):
        return _gen_border_none(width, height, position, corner_radii, resolution, inner_colour)

    if inner_corner_radius_control:
        return _gen_border_inner(width, height, position, corner_radii, border_thickness, resolution, inner_colour, border_colour, gradient)
    return _gen_border_outer(width, height, position, corner_radii, border_thickness, resolution, inner_colour, border_colour, gradient)

def _gen_border_outer(
        width: float,
        height: float,
        position: Vec2,
        corner_radii: tuple[float, float, float, float],
        border_thickness: tuple[float, float, float, float],
        resolution: int,
        inner_colour: RGBA255,
        border_colour: RGBA255,
        gradient: bool = False,
    ):
    border_indices = []
    internal_indices = []
    r2 = 2 * resolution
    c = 4 * resolution
    c2 = 2 * c
    c3 = 3 * c

    for x_a in range(0, r2 - 1):
        x_b = x_a + r2
        border_indices.extend((x_a, x_a + 1, x_a + c, x_a + 1, x_a + c + 1, x_a + c)) # top pair
        border_indices.extend((x_b, x_b + 1, x_b + c, x_b + 1, x_b + c + 1, x_b + c)) # bottom pair
    
        x_c = x_a + c2
        internal_indices.extend((x_c, x_c + 1, c3 - x_a - 1, x_c + 1, c3 - x_a - 2, c3 - x_a - 1))

    # final triangle pairings
    border_indices.extend((r2 - 1, r2, r2 - 1 + c, r2, r2 + c, r2 - 1 + c))
    border_indices.extend((c - 1, 0, c2 - 1, 0, c, c2 - 1))

    indices = border_indices + internal_indices

    outer_radii = corner_radii
    outer_locations = _find_corner_positions(width, height, position, outer_radii)
    

    inner_pos = position + Vec2((border_thickness[0] - border_thickness[1]), (border_thickness[2] - border_thickness[3]))
    inner_width = width - border_thickness[0] - border_thickness[1]
    inner_height = height - border_thickness[2] - border_thickness[3]

    # todo ask digi about how to handle changing border thickness when using inner radius 
    inner_radii = (
        max(0.0, corner_radii[0] - max(border_thickness[0], border_thickness[3])), # top left
        max(0.0, corner_radii[1] - max(border_thickness[3], border_thickness[1])), # top right
        max(0.0, corner_radii[2] - max(border_thickness[1], border_thickness[2])), # bottom right
        max(0.0, corner_radii[3] - max(border_thickness[2], border_thickness[0])), # bottom left
    )
    inner_locations = _find_corner_positions(inner_width, inner_height, inner_pos, inner_radii)

    arc_resolution = QUARTER_ARC_RADIANS / (resolution - 1)
    points = [None] * resolution * 12
    colours = [None] * resolution * 12

    for corner in range(4):
        inner_location = inner_locations[corner]
        inner_radius = inner_radii[corner]
        outer_location = outer_locations[corner]
        outer_radius = outer_radii[corner]
        for vertex in range(resolution):
            idx = vertex + corner * resolution
            theta = vertex * arc_resolution + QUARTER_ARC_RADIANS * corner
            x, y = -cos(theta), sin(theta)
            points[idx] = outer_location + Vec2(outer_radius * x, outer_radius * y)
            points[idx + c] = points[idx + c2] = inner_location + Vec2(inner_radius * x, inner_radius * y)

            colours[idx] = border_colour
            colours[idx + c] = inner_colour if gradient else border_colour
            colours[idx + c2] = inner_colour 

    return indices, points, colours

def _gen_border_inner(
        width: float,
        height: float,
        position: Vec2,
        corner_radii: tuple[float, float, float, float],
        border_thickness: tuple[float, float, float, float],
        resolution: int,
        inner_colour: RGBA255,
        border_colour: RGBA255,
        gradient: bool = False,
    ):
    border_indices = []
    internal_indices = []
    r2 = 2 * resolution
    c = 4 * resolution
    c2 = 2 * c
    c3 = 3 * c

    for x_a in range(0, r2 - 1):
        x_b = x_a + r2
        border_indices.extend((x_a, x_a + 1, x_a + c, x_a + 1, x_a + c + 1, x_a + c)) # top pair
        border_indices.extend((x_b, x_b + 1, x_b + c, x_b + 1, x_b + c + 1, x_b + c)) # bottom pair
    
        x_c = x_a + c2
        internal_indices.extend((x_c, x_c + 1, c3 - x_a - 1, x_c + 1, c3 - x_a - 2, c3 - x_a - 1))

    # final triangle pairings
    border_indices.extend((r2 - 1, r2, r2 - 1 + c, r2, r2 + c, r2 - 1 + c))
    border_indices.extend((c - 1, 0, c2 - 1, 0, c, c2 - 1))

    indices = border_indices + internal_indices

    inner_pos = position + Vec2((border_thickness[0] - border_thickness[1]), (border_thickness[2] - border_thickness[3]))
    inner_width = width - border_thickness[0] - border_thickness[1]
    inner_height = height - border_thickness[2] - border_thickness[3]

    locations = _find_corner_positions(inner_width, inner_height, inner_pos, corner_radii)
    # todo ask digi about how to handle changing border thickness when using inner radius 
    outer_radii = (
        max(border_thickness[0], border_thickness[3]) + corner_radii[0], # top left
        max(border_thickness[3], border_thickness[1]) + corner_radii[1], # top right
        max(border_thickness[1], border_thickness[2]) + corner_radii[2], # bottom right
        max(border_thickness[2], border_thickness[0]) + corner_radii[3], # bottom left
    )
    outer_locations = _find_corner_positions(width, height, position, outer_radii)
    
    arc_resolution = QUARTER_ARC_RADIANS / (resolution - 1)
    points = [None] * resolution * 12
    colours = [None] * resolution * 12
    for corner in range(4):
        inner_location = locations[corner]
        inner_radius = corner_radii[0]
        outer_location = outer_locations[corner]
        outer_radius = outer_radii[corner]
        for vertex in range(resolution):
            idx = vertex + corner * resolution
            theta = vertex * arc_resolution + QUARTER_ARC_RADIANS * corner
            x, y = -cos(theta), sin(theta)
            points[idx] = outer_location + Vec2(outer_radius * x, outer_radius * y)
            points[idx + c] = points[idx + c2] = inner_location + Vec2(inner_radius * x, inner_radius * y)

            colours[idx] = border_colour
            colours[idx + c] = inner_colour if gradient else border_colour
            colours[idx + c2] = inner_colour 

    return indices, points, colours

def _gen_border_none(
        width: float,
        height: float,
        position: Vec2,
        corner_radii: tuple[float, float, float, float],
        resolution: int,
        inner_colour: RGBA255,
    ):
    count = 4 * resolution
    indices = []
    for vertex in range(2 * resolution - 1):
        indices.extend((vertex, vertex + 1, count - vertex - 1, vertex + 1, count - vertex - 2, count - vertex - 1))
    

    locations = _find_corner_positions(width, height, position, corner_radii)
    arc_resolution = QUARTER_ARC_RADIANS / (resolution - 1)
    points = []

    for corner in range(4):
        location = locations[corner]
        radius = corner_radii[corner]
        for vertex in range(resolution):
            theta = vertex * arc_resolution + corner * QUARTER_ARC_RADIANS
            points.append(location + Vec2(-cos(theta) * radius, sin(theta) * radius))

    colours = [inner_colour] * count

    return indices, points, colours

def _find_corner_positions(width: float, height: float, position: Vec2, radii: tuple[float, float, float, float]):
    hw = width / 2.0
    hh = height / 2.0
    top_left = position + Vec2(radii[0] - hw, hh - radii[0])
    top_right = position + Vec2(hw - radii[1], hh - radii[1])
    bottom_right = position + Vec2(hw - radii[2], radii[2] - hh)
    bottom_left = position + Vec2(radii[3] - hw, radii[3] - hh)

    return top_left, top_right, bottom_right, bottom_left
