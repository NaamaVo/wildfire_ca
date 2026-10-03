import math
import numpy as np

from config import FireConfig, GridConfig
from geometry import calculate_slope_angle, calculate_theta_ij, iter_neighbors
from models import SimulationDiagnostics, SimulationResult, WindField
from wind import get_edge_wind


def calculate_wind_factor(
    beta_w: float,
    wind_speed: float,
    wind_direction: float,
    spread_direction: float
) -> float:
    """Calculates directional wind multiplier Kw."""
    return math.exp(
        beta_w
        * wind_speed
        * math.cos(wind_direction - spread_direction)
    )


def calculate_slope_factor(
    beta_s: float,
    phi_ij: float,
    slope_offset: float
) -> float:
    """Calculates directional slope multiplier Ks."""
    return math.exp(
        beta_s
        * (math.tan(phi_ij) + slope_offset)
    )


def calculate_moisture_factor(
    beta_m: float,
    moisture_j: float,
    use_moisture: bool = True
) -> float:
    """
    Calculates fuel-moisture multiplier Km for target cell j.
    
    Km = exp(-beta_m * M_j) when use_moisture is True, else 1.0.
    """
    if not use_moisture:
        return 1.0
    return math.exp(-beta_m * moisture_j)


def calculate_spread_probability(
    p0: float,
    kw: float,
    ks: float,
    km: float = 1.0
) -> tuple[float, bool]:
    """
    Calculates single-edge spread probability P_ij.
    
    Returns
    -------
    tuple[float, bool]
        (p_clipped, was_clipped) where was_clipped is True if P_raw > 1.0.
    """
    p_raw = p0 * kw * ks * km
    was_clipped = bool(p_raw > 1.0)
    p_clipped = float(np.clip(p_raw, 0.0, 1.0))
    return p_clipped, was_clipped


def create_initial_state(grid: GridConfig) -> np.ndarray:
    state = np.zeros((grid.rows, grid.cols), dtype=int)

    center_row = grid.rows // 2
    center_col = grid.cols // 2

    state[center_row, center_col] = 1
    return state


def run_simulation(
    elevation: np.ndarray,
    wind: WindField,
    moisture: np.ndarray,
    grid: GridConfig,
    fire: FireConfig
) -> SimulationResult:

    rng = np.random.default_rng(fire.random_seed)

    state = create_initial_state(grid)
    state_history = [state.copy()]
    diagnostics = []

    for time_step in range(1, grid.num_steps + 1):

        j_is_not_burn = np.ones((grid.rows, grid.cols), dtype=float)

        kw_values = []
        ks_values = []
        km_values = []
        active_moistures = []

        edges_evaluated = 0
        edges_clipped = 0

        burning_cells = np.argwhere(state == 1)

        for i_row, i_col in burning_cells:

            i_row = int(i_row)
            i_col = int(i_col)

            for j_row, j_col in iter_neighbors(
                i_row,
                i_col,
                grid.rows,
                grid.cols
            ):

                if state[j_row, j_col] != 0:
                    continue

                edges_evaluated += 1

                theta_ij = calculate_theta_ij(
                    i_row,
                    i_col,
                    j_row,
                    j_col
                )

                wind_speed, wind_direction = get_edge_wind(
                    wind,
                    i_row,
                    i_col,
                    j_row,
                    j_col
                )

                kw = calculate_wind_factor(
                    fire.beta_w,
                    wind_speed,
                    wind_direction,
                    theta_ij
                )

                phi_ij = calculate_slope_angle(
                    i_row,
                    i_col,
                    j_row,
                    j_col,
                    elevation,
                    grid.cell_size_m
                )

                ks = calculate_slope_factor(
                    fire.beta_s,
                    phi_ij,
                    fire.slope_offset
                )

                m_j = float(moisture[j_row, j_col])
                km = calculate_moisture_factor(
                    fire.beta_m,
                    m_j,
                    use_moisture=fire.use_moisture
                )

                p_ij, was_clipped = calculate_spread_probability(
                    fire.p0,
                    kw,
                    ks,
                    km=km
                )

                if was_clipped:
                    edges_clipped += 1

                j_is_not_burn[j_row, j_col] *= (1.0 - p_ij)

                kw_values.append(kw)
                ks_values.append(ks)
                km_values.append(km)
                active_moistures.append(m_j)

        p_burn = 1.0 - j_is_not_burn

        random_draws = rng.random((grid.rows, grid.cols))
        can_ignite = state == 0
        ignites = can_ignite & (random_draws < p_burn)

        new_state = state.copy()
        new_state[ignites] = 1

        state = new_state
        state_history.append(state.copy())

        clip_frac = (
            edges_clipped / edges_evaluated
            if edges_evaluated > 0
            else 0.0
        )

        diagnostics.append(
            SimulationDiagnostics(
                time_step=time_step,
                burning_cells=int(state.sum()),
                kw_min=min(kw_values) if kw_values else None,
                kw_max=max(kw_values) if kw_values else None,
                ks_min=min(ks_values) if ks_values else None,
                ks_max=max(ks_values) if ks_values else None,
                km_min=min(km_values) if km_values else None,
                km_max=max(km_values) if km_values else None,
                moisture_min=min(active_moistures) if active_moistures else None,
                moisture_max=max(active_moistures) if active_moistures else None,
                edges_evaluated=edges_evaluated,
                edges_clipped=edges_clipped,
                clip_fraction=clip_frac,
            )
        )

    return SimulationResult(
        state_history=state_history,
        diagnostics=diagnostics
    )
