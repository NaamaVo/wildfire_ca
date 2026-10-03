import math
import numpy as np

from config import GridConfig, WindConfig
from models import WindField


def generate_wind_field(grid: GridConfig, cfg: WindConfig) -> WindField:
    rng = np.random.default_rng(cfg.seed)

    x = np.arange(grid.cols)
    y = np.arange(grid.rows)
    X, Y = np.meshgrid(x, y)

    speed_change = np.zeros((grid.rows, grid.cols), dtype=float)
    direction_change = np.zeros((grid.rows, grid.cols), dtype=float)

    for _ in range(cfg.num_features):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        sigma = rng.uniform(7, 18)

        influence = np.exp(
            -((X - center_x) ** 2 + (Y - center_y) ** 2)
            / (2 * sigma ** 2)
        )

        speed_change += rng.uniform(
            -cfg.max_speed_variation_mps,
            cfg.max_speed_variation_mps
        ) * influence

        direction_change += rng.uniform(
            -cfg.max_direction_variation_rad,
            cfg.max_direction_variation_rad
        ) * influence

    speed_change = np.clip(
        speed_change,
        -cfg.max_speed_variation_mps,
        cfg.max_speed_variation_mps
    )

    direction_change = np.clip(
        direction_change,
        -cfg.max_direction_variation_rad,
        cfg.max_direction_variation_rad
    )

    speed = np.clip(cfg.base_speed_mps + speed_change, 0.5, None)
    direction = cfg.base_direction_rad + direction_change

    u = speed * np.cos(direction)
    v = speed * np.sin(direction)

    return WindField(u=u, v=v, speed=speed, direction=direction)


def get_edge_wind(
    wind: WindField,
    i_row: int,
    i_col: int,
    j_row: int,
    j_col: int
) -> tuple[float, float]:

    u_local = (wind.u[i_row, i_col] + wind.u[j_row, j_col]) / 2.0
    v_local = (wind.v[i_row, i_col] + wind.v[j_row, j_col]) / 2.0

    speed = math.hypot(u_local, v_local)
    direction = math.atan2(v_local, u_local)

    return speed, direction
