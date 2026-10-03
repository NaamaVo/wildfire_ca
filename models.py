from dataclasses import dataclass
import numpy as np


@dataclass
class WindField:
    u: np.ndarray
    v: np.ndarray
    speed: np.ndarray
    direction: np.ndarray


@dataclass
class SimulationDiagnostics:
    time_step: int
    burning_cells: int
    burned_cells: int
    unburned_cells: int
    newly_ignited_cells: int
    kw_min: float | None
    kw_max: float | None
    ks_min: float | None
    ks_max: float | None
    km_min: float | None
    km_max: float | None
    moisture_min: float | None
    moisture_max: float | None
    edges_evaluated: int = 0
    edges_clipped: int = 0
    clip_fraction: float = 0.0


@dataclass
class SimulationResult:
    state_history: list[np.ndarray]
    diagnostics: list[SimulationDiagnostics]
