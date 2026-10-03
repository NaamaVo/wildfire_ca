import math
import numpy as np


NEIGHBOR_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


def iter_neighbors(row: int, col: int, rows: int, cols: int):
    for d_row, d_col in NEIGHBOR_OFFSETS:
        j_row = row + d_row
        j_col = col + d_col

        if 0 <= j_row < rows and 0 <= j_col < cols:
            yield j_row, j_col


def calculate_theta_ij(
    i_row: int,
    i_col: int,
    j_row: int,
    j_col: int
) -> float:
    dx = j_col - i_col
    dy = i_row - j_row
    return math.atan2(dy, dx)


def calculate_slope_angle(
    i_row: int,
    i_col: int,
    j_row: int,
    j_col: int,
    elevation: np.ndarray,
    cell_size_m: float
) -> float:

    delta_height = elevation[j_row, j_col] - elevation[i_row, i_col]

    delta_row = j_row - i_row
    delta_col = j_col - i_col

    horizontal_distance = cell_size_m * math.hypot(
        delta_row,
        delta_col
    )

    return math.atan(delta_height / horizontal_distance)
