from pyglet.math import Vec2

PointList = list[Vec2]


def snap(point: Vec2, step: float, x_offset: float = 0.0, y_offset: float = 0.0) -> Vec2:
    return Vec2(int(point.x / step), int(point.y / step)) * step + Vec2(x_offset % step + (step / 2), y_offset % step + (step / 2) - step)


def dda(start: Vec2, end: Vec2) -> PointList:
    points: PointList = []

    dx = end.x - start.x
    dy = end.y - start.y

    # Number of steps in the loop needed to draw the whole line
    steps = int(abs(dx)) if abs(dx) > abs(dy) else int(abs(dy))

    if steps < 1:
        return [start, end]

    # Rise and rtun
    x_inc = float(dx / steps)
    y_inc = float(dy / steps)

    px = start.x
    py = start.y

    # Gen points
    for _ in range(0, steps + 1):
        points.append(Vec2(px, py))
        px += x_inc
        py += y_inc

    return points
