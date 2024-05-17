from typing import NamedTuple
from math import floor


class DDAPoint(NamedTuple):
    x: int
    y: int
    z: int
    d: float


class DDAResult(NamedTuple):
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    d: float
    path: tuple[DDAPoint, ...]


def dda(x: float, y: float, z: float, d_x: float, d_y: float, d_z: float, bounds_x: int, bounds_y: int, bounds_z: int) -> DDAResult:
    i_x, i_y, i_z = int(floor(x)), int(floor(y)), int(floor(z))  # grid indices (index coord)

    # distance traveled when moving 1 unit along the x, y, and z axis (change in parametric value t at coord)
    dt_x = float('inf') if d_x == 0 else 1.0 / abs(d_x)
    dt_y = float('inf') if d_y == 0 else 1.0 / abs(d_y)
    dt_z = float('inf') if d_z == 0 else 1.0 / abs(d_z)

    # distance traveled when moving to the edge of the starting pos along the x, y, and z axis. (parametric value t at coord)
    t_x = ((1.0 - (x % 1)) if d_x >= 0.0 else (x % 1)) * dt_x
    t_y = ((1.0 - (y % 1)) if d_y >= 0.0 else (y % 1)) * dt_y
    t_z = ((1.0 - (z % 1)) if d_z >= 0.0 else (z % 1)) * dt_z

    # the index step when moving along the x, y, and z axis. (start_coord)
    s_x = 1 if d_x >= 0.0 else -1
    s_y = 1 if d_y >= 0.0 else -1
    s_z = 1 if d_z >= 0.0 else -1

    t = 0.0
    t_o = 0.0
    n_x, n_y, n_z = i_x, i_y, i_z  # (next coord)
    l_x, l_y, l_z = i_x, i_y, i_z  # (last coord)
    path = []
    while True:
        if t_x < min(t_y, t_z):
            t = t_x
            t_x += dt_x
            n_x += s_x
        elif t_y < min(t_x, t_z):
            t = t_y
            t_y += dt_y
            n_y += s_y
        else:
            t = t_z
            t_z += dt_z
            n_z += s_z

        path.append(DDAPoint(l_x, l_y, l_z, t - t_o))
        if not (0 <= n_x < bounds_x) or not (0 <= n_y < bounds_y) or not (0 <= n_z < bounds_z):
            # If we stepped out of bounds we want to quit.
            break
        l_x, l_y, l_z = n_x, n_y, n_z
        t_o = t

    start = path[0]
    end = path[-1]
    d = t
    return DDAResult(
        start[0], start[1], start[2],
        end[0], end[1], end[2],
        d, tuple(path)
    )
