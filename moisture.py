"""
Fuel Moisture Field Generator Module
Generates synthetic, spatially smooth 2D fuel-moisture maps.
"""

import numpy as np
from config import GridConfig, MoistureConfig


def generate_moisture_field(
    grid: GridConfig,
    cfg: MoistureConfig
) -> np.ndarray:
    """
    Generates a spatially smooth 2D synthetic fuel-moisture field.
    
    Parameters
    ----------
    grid : GridConfig
        Spatial grid configuration (rows, cols).
    cfg : MoistureConfig
        Moisture generation configuration.

    Returns
    -------
    np.ndarray
        2D array of shape (rows, cols) containing fuel moisture fractions
        clipped to [min_moisture, max_moisture].
    """
    rng = np.random.default_rng(cfg.seed)

    x = np.arange(grid.cols)
    y = np.arange(grid.rows)
    X, Y = np.meshgrid(x, y)

    # Start from configured baseline moisture
    moisture = np.full(
        (grid.rows, grid.cols),
        cfg.base_moisture,
        dtype=float
    )

    # Add smooth Gaussian perturbations (wetter and drier patches)
    for _ in range(cfg.num_features):
        center_x = rng.uniform(0, grid.cols)
        center_y = rng.uniform(0, grid.rows)
        sigma = rng.uniform(cfg.sigma_min, cfg.sigma_max)

        influence = np.exp(
            -((X - center_x) ** 2 + (Y - center_y) ** 2)
            / (2 * sigma ** 2)
        )

        delta_m = rng.uniform(
            -cfg.max_moisture_variation,
            cfg.max_moisture_variation
        )

        moisture += delta_m * influence

    # Clip values into configured prototype physical bounds
    moisture = np.clip(
        moisture,
        cfg.min_moisture,
        cfg.max_moisture
    )

    return moisture
