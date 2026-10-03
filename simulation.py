import math
import numpy as np

from config import (
    STATE_BURNED,
    STATE_BURNING,
    STATE_UNBURNED,
    FireConfig,
    GridConfig,
)
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
    """
    Creates the initial state matrix:
      0 = Not burning / Unburned
      1 = Burning (center cell initialized to 1)
     -1 = Burned
    """
    state = np.full((grid.rows, grid.cols), STATE_UNBURNED, dtype=int)

    center_row = grid.rows // 2
    center_col = grid.cols // 2

    state[center_row, center_col] = STATE_BURNING
    return state


def run_simulation(
    elevation: np.ndarray,
    wind: WindField,
    moisture: np.ndarray,
    grid: GridConfig,
    fire: FireConfig
) -> SimulationResult:
    """
    Runs the cellular automaton wildfire simulation with 3 states:
      0  = Not burning (Unburned)
      1  = Burning
      -1 = Burned

    Burnout Logic:
      - For each currently burning cell (1), draw r ~ Uniform(0, 1).
      - If r < Pcontinue (fire.p_continue), the cell remains burning (1).
      - Otherwise, it transitions to burned (-1).
      - Burned cells (-1) cannot spread fire and cannot reignite.
    """
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

        # Query all currently burning cells (state == 1)
        burning_cells = np.argwhere(state == STATE_BURNING)

        for i_row, i_col in burning_cells:

            i_row = int(i_row)
            i_col = int(i_col)

            for j_row, j_col in iter_neighbors(
                i_row,
                i_col,
                grid.rows,
                grid.cols
            ):

                # Only unburned neighbors (state == 0) can ignite
                if state[j_row, j_col] != STATE_UNBURNED:
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

        # 1. Stochastic ignition for unburned cells (0 -> 1)
        p_burn = 1.0 - j_is_not_burn
        ignition_draws = rng.random((grid.rows, grid.cols))
        can_ignite = (state == STATE_UNBURNED)
        ignites = can_ignite & (ignition_draws < p_burn)

        # 2. Stochastic burnout for burning cells (1 -> 1 or -1)
        # For each cell currently burning:
        # If r < Pcontinue -> remains burning (1), else -> transitions to burned (-1)
        burnout_draws = rng.random((grid.rows, grid.cols))
        is_burning = (state == STATE_BURNING)
        extinguishes = is_burning & (burnout_draws >= fire.p_continue)

        # 3. Synchronous State Update
        new_state = state.copy()
        new_state[extinguishes] = STATE_BURNED
        new_state[ignites] = STATE_BURNING

        state = new_state
        state_history.append(state.copy())

        clip_frac = (
            edges_clipped / edges_evaluated
            if edges_evaluated > 0
            else 0.0
        )

        num_burning = int(np.count_nonzero(state == STATE_BURNING))
        num_burned = int(np.count_nonzero(state == STATE_BURNED))
        num_unburned = int(np.count_nonzero(state == STATE_UNBURNED))
        num_newly_ignited = int(np.count_nonzero(ignites))

        diagnostics.append(
            SimulationDiagnostics(
                time_step=time_step,
                burning_cells=num_burning,
                burned_cells=num_burned,
                unburned_cells=num_unburned,
                newly_ignited_cells=num_newly_ignited,
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
