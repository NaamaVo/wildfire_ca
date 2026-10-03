import os
import matplotlib.pyplot as plt
import numpy as np

from config import (
    FireConfig,
    GridConfig,
    MoistureConfig,
    OutputConfig,
    TerrainConfig,
    WindConfig,
)
from moisture import generate_moisture_field
from simulation import calculate_moisture_factor, run_simulation
from terrain import generate_topography
from visualization import create_simulation_animation, save_animation
from wind import generate_wind_field


def main():

    grid_cfg = GridConfig()
    terrain_cfg = TerrainConfig()
    wind_cfg = WindConfig()
    moisture_cfg = MoistureConfig()
    fire_cfg = FireConfig()
    output_cfg = OutputConfig()

    # 1. Environmental Layer Generation
    elevation = generate_topography(
        grid_cfg,
        terrain_cfg
    )

    wind = generate_wind_field(
        grid_cfg,
        wind_cfg
    )

    moisture = generate_moisture_field(
        grid_cfg,
        moisture_cfg
    )

    # Global Environmental Statistics
    m_min, m_max = float(moisture.min()), float(moisture.max())
    km_at_m_max = calculate_moisture_factor(fire_cfg.beta_m, m_max, fire_cfg.use_moisture)
    km_at_m_min = calculate_moisture_factor(fire_cfg.beta_m, m_min, fire_cfg.use_moisture)

    print("================ ENVIRONMENTAL MAP STATISTICS ================")
    print(f"Topography elevation range: {elevation.min():.1f}m - {elevation.max():.1f}m")
    print(f"Wind speed range: {wind.speed.min():.2f}m/s - {wind.speed.max():.2f}m/s")
    print(f"Fuel moisture (M) range: {m_min:.4f} ({m_min*100:.1f}%) - {m_max:.4f} ({m_max*100:.1f}%)")
    print(f"Global Km range (wettest -> driest): {km_at_m_max:.4f} - {km_at_m_min:.4f} (beta_m={fire_cfg.beta_m})")

    # 2. Run Simulation
    result = run_simulation(
        elevation=elevation,
        wind=wind,
        moisture=moisture,
        grid=grid_cfg,
        fire=fire_cfg
    )

    # 3. Aggregate Edge & Clipping Diagnostics
    total_edges_eval = sum(d.edges_evaluated for d in result.diagnostics)
    total_edges_clipped = sum(d.edges_clipped for d in result.diagnostics)
    overall_clip_fraction = (
        total_edges_clipped / total_edges_eval
        if total_edges_eval > 0
        else 0.0
    )

    if result.diagnostics:
        final = result.diagnostics[-1]
        total_grid_cells = grid_cfg.rows * grid_cfg.cols
        total_burned_footprint = final.burned_cells + final.burning_cells
        print("\n================ SIMULATION DIAGNOSTICS ================")
        print(f"Time Step: T = {grid_cfg.num_steps}")
        print(f"Active Burning Cells (State 1)  : {final.burning_cells}")
        print(f"Burned Cells (State -1)         : {final.burned_cells}")
        print(f"Total Affected Footprint        : {total_burned_footprint} / {total_grid_cells} ({total_burned_footprint / total_grid_cells * 100:.2f}%)")
        print(f"Remaining Unburned Cells (0)    : {final.unburned_cells} / {total_grid_cells}")
        print(f"Total directed edges evaluated  : {total_edges_eval}")
        print(f"Total edges clipped (P_raw > 1) : {total_edges_clipped} ({overall_clip_fraction * 100:.2f}%)")

    # 4. Visualization & Animation Export
    fig, animation = create_simulation_animation(
        elevation=elevation,
        wind=wind,
        moisture=moisture,
        result=result,
        grid_cfg=grid_cfg,
        terrain_cfg=terrain_cfg,
        wind_cfg=wind_cfg,
        moisture_cfg=moisture_cfg,
        output_cfg=output_cfg
    )

    save_animation(
        animation,
        output_cfg
    )

    print("\nAnimation saved at:")
    print(os.path.abspath(output_cfg.gif_filename))

    plt.show()


if __name__ == "__main__":
    main()
