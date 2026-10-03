import numpy as np
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

from config import (
    GridConfig,
    MoistureConfig,
    OutputConfig,
    TerrainConfig,
    WindConfig,
)
from models import SimulationResult, WindField


# Colormap mapping for 3 states:
#  -1 = Burned (Brown)
#   0 = Not Burning / Unburned (Green)
#   1 = Burning (Red)
FIRE_CMAP = ListedColormap(["#8B5A2B", "#2E7D32", "#D32F2F"])
FIRE_NORM = BoundaryNorm(boundaries=[-1.5, -0.5, 0.5, 1.5], ncolors=3)


def create_simulation_animation(
    elevation: np.ndarray,
    wind: WindField,
    moisture: np.ndarray,
    result: SimulationResult,
    grid_cfg: GridConfig,
    terrain_cfg: TerrainConfig,
    wind_cfg: WindConfig,
    moisture_cfg: MoistureConfig,
    output_cfg: OutputConfig
):
    fig, (ax_topo, ax_wind, ax_moist, ax_fire) = plt.subplots(
        1,
        4,
        figsize=(22, 6)
    )

    # 1. Topography Panel
    topo_image = ax_topo.imshow(
        elevation,
        cmap="terrain",
        vmin=terrain_cfg.min_elevation_m,
        vmax=terrain_cfg.max_elevation_m
    )

    topo_cbar = fig.colorbar(
        topo_image,
        ax=ax_topo,
        fraction=0.046,
        pad=0.04
    )
    topo_cbar.set_label("Elevation (m)")
    ax_topo.set_title("Topography")

    center_row = grid_cfg.rows // 2
    center_col = grid_cfg.cols // 2

    ax_topo.scatter(
        center_col,
        center_row,
        marker="*",
        s=150,
        color="red",
        edgecolor="black",
        label="Initial ignition"
    )
    ax_topo.legend(loc="upper right")

    # 2. Wind Field Panel
    wind_image = ax_wind.imshow(
        wind.speed,
        cmap="viridis"
    )

    wind_cbar = fig.colorbar(
        wind_image,
        ax=ax_wind,
        fraction=0.046,
        pad=0.04
    )
    wind_cbar.set_label("Wind speed (m/s)")
    ax_wind.set_title("Wind Field")

    Y, X = np.mgrid[0:grid_cfg.rows, 0:grid_cfg.cols]
    step = wind_cfg.arrow_step

    ax_wind.quiver(
        X[::step, ::step],
        Y[::step, ::step],
        wind.u[::step, ::step],
        -wind.v[::step, ::step],
        pivot="middle"
    )

    # 3. Fuel Moisture Panel
    moist_image = ax_moist.imshow(
        moisture,
        cmap="YlGnBu",
        vmin=moisture_cfg.min_moisture,
        vmax=moisture_cfg.max_moisture
    )

    moist_cbar = fig.colorbar(
        moist_image,
        ax=ax_moist,
        fraction=0.046,
        pad=0.04
    )
    moist_cbar.set_label("Fuel Moisture Fraction")
    ax_moist.set_title("Fuel Moisture (M)")

    # 4. Fire Spread Panel (3 states: -1=Burned (brown), 0=Not Burning (green), 1=Burning (red))
    fire_image = ax_fire.imshow(
        result.state_history[0],
        cmap=FIRE_CMAP,
        norm=FIRE_NORM
    )

    ax_fire.set_title("Wildfire Spread - T = 0")

    ax_fire.set_xticks(
        np.arange(-0.5, grid_cfg.cols, 1),
        minor=True
    )
    ax_fire.set_yticks(
        np.arange(-0.5, grid_cfg.rows, 1),
        minor=True
    )
    ax_fire.grid(
        which="minor",
        linewidth=0.15
    )
    ax_fire.tick_params(
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )

    legend_elements = [
        Patch(
            facecolor="#2E7D32",
            edgecolor="black",
            label="Not Burning (0)"
        ),
        Patch(
            facecolor="#D32F2F",
            edgecolor="black",
            label="Burning (1)"
        ),
        Patch(
            facecolor="#8B5A2B",
            edgecolor="black",
            label="Burned (-1)"
        )
    ]

    ax_fire.legend(
        handles=legend_elements,
        loc="upper left",
        bbox_to_anchor=(1.02, 1)
    )

    def update(frame):
        fire_image.set_array(result.state_history[frame])
        diag = result.diagnostics[frame - 1] if frame > 0 else None
        if diag:
            ax_fire.set_title(
                f"Wildfire Spread - T = {frame}\n"
                f"(Active: {diag.burning_cells}, Burned: {diag.burned_cells})"
            )
        else:
            ax_fire.set_title("Wildfire Spread - T = 0 (Active: 1)")
        return [fire_image]

    animation = FuncAnimation(
        fig,
        update,
        frames=len(result.state_history),
        interval=output_cfg.frame_interval_ms,
        blit=False,
        repeat=True
    )

    fig.suptitle(
        "Wildfire Simulation: Topography + Wind + Moisture + Fire",
        fontsize=16
    )

    fig.tight_layout()

    return fig, animation


def save_animation(animation, output_cfg: OutputConfig):
    animation.save(
        output_cfg.gif_filename,
        writer=PillowWriter(fps=output_cfg.fps)
    )
