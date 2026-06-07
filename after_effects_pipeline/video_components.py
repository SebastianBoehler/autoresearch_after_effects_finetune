from __future__ import annotations


FOREGROUND_DELTA = 90


def foreground_component_metrics(
    frame: bytes,
    width: int,
    height: int,
    bg_r: float,
    bg_g: float,
    bg_b: float,
    *,
    stride: int = 2,
) -> dict[str, float]:
    grid_width = (width + stride - 1) // stride
    grid_height = (height + stride - 1) // stride
    foreground = _foreground_grid(
        frame,
        width,
        height,
        bg_r,
        bg_g,
        bg_b,
        stride=stride,
        grid_width=grid_width,
        grid_height=grid_height,
    )
    total = grid_width * grid_height
    foreground_count = sum(1 for value in foreground if value)
    if foreground_count == 0:
        return {
            "component_count": 0.0,
            "largest_component_ratio": 0.0,
            "largest_component_share": 0.0,
            "edge_touch_component_ratio": 0.0,
        }

    seen = [False] * len(foreground)
    component_count = 0
    largest = 0
    edge_touching = 0
    for index, is_foreground in enumerate(foreground):
        if not is_foreground or seen[index]:
            continue
        size, touches_edge = _visit_component(
            foreground,
            seen,
            index,
            grid_width,
            grid_height,
        )
        component_count += 1
        largest = max(largest, size)
        if touches_edge:
            edge_touching += 1

    return {
        "component_count": float(component_count),
        "largest_component_ratio": largest / total,
        "largest_component_share": largest / foreground_count,
        "edge_touch_component_ratio": edge_touching / component_count,
    }


def _foreground_grid(
    frame: bytes,
    width: int,
    height: int,
    bg_r: float,
    bg_g: float,
    bg_b: float,
    *,
    stride: int,
    grid_width: int,
    grid_height: int,
) -> list[bool]:
    grid = []
    for gy in range(grid_height):
        y = min(height - 1, gy * stride)
        for gx in range(grid_width):
            x = min(width - 1, gx * stride)
            index = (y * width + x) * 3
            delta = (
                abs(frame[index] - bg_r)
                + abs(frame[index + 1] - bg_g)
                + abs(frame[index + 2] - bg_b)
            )
            grid.append(delta > FOREGROUND_DELTA)
    return grid


def _visit_component(
    foreground: list[bool],
    seen: list[bool],
    start: int,
    grid_width: int,
    grid_height: int,
) -> tuple[int, bool]:
    stack = [start]
    seen[start] = True
    size = 0
    touches_edge = False
    while stack:
        index = stack.pop()
        size += 1
        x = index % grid_width
        y = index // grid_width
        if x == 0 or y == 0 or x == grid_width - 1 or y == grid_height - 1:
            touches_edge = True
        for neighbor in _neighbors(index, x, y, grid_width, grid_height):
            if foreground[neighbor] and not seen[neighbor]:
                seen[neighbor] = True
                stack.append(neighbor)
    return size, touches_edge


def _neighbors(
    index: int,
    x: int,
    y: int,
    grid_width: int,
    grid_height: int,
):
    if x > 0:
        yield index - 1
    if x < grid_width - 1:
        yield index + 1
    if y > 0:
        yield index - grid_width
    if y < grid_height - 1:
        yield index + grid_width
