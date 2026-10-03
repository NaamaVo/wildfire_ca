import numpy as np
from config import GridConfig, TerrainConfig


def generate_topography(grid: GridConfig, cfg: TerrainConfig) -> np.ndarray:
    rng = np.random.default_rng(cfg.seed)

    x = np.arange(grid.cols)
    y = np.arange(grid.rows)
    X, Y = np.meshgrid(x, y)

    elevation = np.zeros((grid.rows, grid.cols), dtype=float)

    for _ in range(cfg.num_large_mountains):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        amplitude = rng.uniform(700, 1500)
        sigma = rng.uniform(8, 16)

        elevation += amplitude * np.exp(
            -((X - center_x) ** 2 + (Y - center_y) ** 2)
            / (2 * sigma ** 2)
        )

    for _ in range(cfg.num_small_hills):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        amplitude = rng.uniform(100, 500)
        sigma = rng.uniform(3, 8)

        elevation += amplitude * np.exp(
            -((X - center_x) ** 2 + (Y - center_y) ** 2)
            / (2 * sigma ** 2)
        )

    for _ in range(cfg.num_valleys):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        amplitude = rng.uniform(-900, -300)
        sigma = rng.uniform(5, 12)

        elevation += amplitude * np.exp(
            -((X - center_x) ** 2 + (Y - center_y) ** 2)
            / (2 * sigma ** 2)
        )

    for _ in range(cfg.num_ridges):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        amplitude = rng.uniform(400, 1000)
        angle = rng.uniform(0, 2 * np.pi)
        sigma_long = rng.uniform(10, 20)
        sigma_short = rng.uniform(2, 5)

        X_shift = X - center_x
        Y_shift = Y - center_y

        X_rot = X_shift * np.cos(angle) + Y_shift * np.sin(angle)
        Y_rot = -X_shift * np.sin(angle) + Y_shift * np.cos(angle)

        elevation += amplitude * np.exp(
            -(
                X_rot ** 2 / (2 * sigma_long ** 2)
                + Y_rot ** 2 / (2 * sigma_short ** 2)
            )
        )

    for _ in range(cfg.num_small_features):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        amplitude = rng.uniform(-150, 150)
        sigma = rng.uniform(2, 5)

        elevation += amplitude * np.exp(
            -((X - center_x) ** 2 + (Y - center_y) ** 2)
            / (2 * sigma ** 2)
        )

    elevation -= elevation.min()
    max_value = elevation.max()

    if max_value > 0:
        elevation /= max_value

    elevation *= (cfg.max_elevation_m - cfg.min_elevation_m)
    elevation += cfg.min_elevation_m

    return elevation
