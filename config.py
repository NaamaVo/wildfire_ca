from dataclasses import dataclass
import math


@dataclass(frozen=True)
class GridConfig:
    rows: int = 50
    cols: int = 50
    num_steps: int = 50
    cell_size_m: float = 30.0


@dataclass(frozen=True)
class TerrainConfig:
    min_elevation_m: float = 0.0
    max_elevation_m: float = 1500.0
    seed: int = 10
    num_large_mountains: int = 6
    num_small_hills: int = 15
    num_valleys: int = 7
    num_ridges: int = 4
    num_small_features: int = 30


@dataclass(frozen=True)
class WindConfig:
    seed: int = 20
    base_speed_mps: float = 6.0
    base_direction_deg: float = 20.0
    num_features: int = 10
    max_speed_variation_mps: float = 2.5
    max_direction_variation_deg: float = 30.0
    arrow_step: int = 4

    @property
    def base_direction_rad(self) -> float:
        return math.radians(self.base_direction_deg)

    @property
    def max_direction_variation_rad(self) -> float:
        return math.radians(self.max_direction_variation_deg)


@dataclass(frozen=True)
class MoistureConfig:
    """
    Configuration for synthetic spatial fuel moisture generation.
    
    Note: The range [0.05, 0.30] represents synthetic fuel-moisture fractions
    for testing CA dynamics in this prototype, not a universal empirical threshold.
    """
    seed: int = 30
    base_moisture: float = 0.15
    min_moisture: float = 0.05
    max_moisture: float = 0.30
    num_features: int = 10
    max_moisture_variation: float = 0.12
    sigma_min: float = 6.0
    sigma_max: float = 16.0


@dataclass(frozen=True)
class FireConfig:
    """
    Wildfire propagation parameters.
    
    Note:
    - P0 is the baseline spread probability at zero moisture (M=0) before wind,
      slope, and moisture adjustments.
    - beta_m = 3.0 is a temporary prototype default (not scientifically calibrated)
      that will be learned/calibrated from data in differentiable stages.
    """
    p0: float = 0.2
    beta_w: float = 1
    beta_s: float = 1
    beta_m: float = 1
    slope_offset: float = 3.0
    use_moisture: bool = True
    random_seed: int | None = None


@dataclass(frozen=True)
class OutputConfig:
    gif_filename: str = "wildfire_topography_wind_moisture.gif"
    fps: int = 2
    frame_interval_ms: int = 500
