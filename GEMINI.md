# Wildfire Cellular Automaton Research Project

## 1. Project purpose

This is a research-oriented Python project for wildfire spread simulation.

The long-term goal is to build a physically informed, stochastic/probabilistic,
differentiable and calibratable cellular automaton for wildfire prediction.

The project is inspired primarily by:

1. PROPAGATOR-style cellular automata for wildfire propagation.
2. PyTorchFire-style differentiable cellular automata and gradient-based calibration.
3. Rothermel fire-spread equations as a future physical rate-of-spread component.

The implementation is currently an early prototype.
Do not treat temporary parameter values or simplified physics as final scientific choices.


# 2. High-level research goal

The final system should eventually:

- represent wildfire propagation on a spatial grid;
- use environmental inputs such as:
  - topography,
  - wind,
  - fuel type,
  - fuel properties,
  - moisture;
- calculate directional fire spread between neighboring cells;
- remain probabilistic/stochastic;
- eventually become differentiable so important parameters can be learned from
  historical wildfire data using gradient descent;
- integrate Rothermel rate-of-spread calculations;
- eventually support real geographic data rather than only synthetic maps.


# 3. Current project structure

The project is intentionally modular.

Current files:

main.py
    Main orchestration entry point.
    It creates the environment, runs the simulation and launches visualization.

config.py
    Contains model configuration and experimental parameters.
    Parameters should normally be changed here rather than hard-coded elsewhere.

models.py
    Contains shared data structures such as WindField,
    SimulationResult and diagnostics.

terrain.py
    Generates the synthetic topography/elevation map.

wind.py
    Generates the spatial wind vector field and provides
    local wind information for cell-to-cell propagation.

moisture.py
    Generates the synthetic spatial fuel-moisture field.

geometry.py
    Contains grid-neighborhood and geometric calculations:
    neighbor lookup, direction theta_ij and slope phi_ij.

simulation.py
    Contains the wildfire propagation logic:
    Kw, Ks, Km, P_ij, probability accumulation and state transitions.

visualization.py
    Contains plotting, wind visualization, topography visualization,
    fuel-moisture visualization, animation and GIF export.

requirements.txt
    Python dependencies.

README.md
    Basic project usage and structure.


# 4. Current grid

Current prototype:

ROWS = 50
COLS = 50

CELL_SIZE = 30 meters

NUM_STEPS = 50

The current grid is a square raster with an 8-cell Moore neighborhood:

NW  N  NE
W   i   E
SW  S  SE

This is temporary.

Long-term architectural plan:
replace the square raster with a hexagonal radius-2 grid:

- 6 first-ring neighbors
- 12 second-ring neighbors
- 18 directed neighbor interactions in total

Do NOT implement the hexagonal conversion unless explicitly requested.
The current square grid should continue working until that stage.


# 5. Current cell state model

Current simplified implementation:

0 = not burning
1 = burning

The initial fire starts at one cell near/in the center of the grid.

Once a cell ignites, it currently remains in state 1.

This is a prototype simplification.

Future model should likely return to three wildfire states:

- BURNABLE
- BURNING
- BURNED

Do not silently introduce the third state unless requested.


# 6. Current propagation probability

For a burning cell i and burnable neighboring cell j:

P_ij = P0 * Kw * Ks * Km

Current base probability:

P0 = 0.2

Currently Km = 1, because moisture has not yet been implemented.

The probability must remain within [0,1].

The current implementation uses clipping:

P_ij = clip(P_ij, 0, 1)

This is temporary and should be monitored because excessive clipping
may hide unrealistic parameter values.


# 7. Combining multiple burning neighbors

A target cell j may have multiple burning neighbors.

For every burning neighbor i:

P(j does not ignite from i) = 1 - P_ij

The probability that j does not ignite from ANY burning neighbor is:

P_not_burn(j) = product_i (1 - P_ij)

Therefore:

P_burn(j) = 1 - product_i (1 - P_ij)

Then sample:

p ~ Uniform(0,1)

If:

p < P_burn(j)

then j ignites.

This aggregation rule is an important part of the current model.
Do not replace it without discussion.


# 8. Topography model

The current system generates a synthetic but spatially smooth elevation map.

Topography must NOT be generated independently per cell.

Neighboring cells should have reasonably similar elevations.

The terrain generator currently combines several spatial features:

- large mountains,
- smaller hills,
- valleys,
- elongated mountain ridges,
- small-scale terrain variations.

The terrain is normalized to approximately:

0–1500 meters.

The terrain uses a fixed random seed so that experiments can use
the SAME topography between simulation runs.

Current topography seed:

TOPOGRAPHY_SEED = 10

Keeping terrain fixed is intentional because it allows parameter comparisons
on the same environment.


# 9. Slope calculation

For propagation from cell i to cell j:

delta_h = elevation_j - elevation_i

The horizontal distance is:

orthogonal neighbor:
    d = CELL_SIZE

diagonal neighbor:
    d = CELL_SIZE * sqrt(2)

More generally:

d_ij = CELL_SIZE * sqrt(delta_row^2 + delta_col^2)

Slope angle:

phi_ij = atan(delta_h / d_ij)

Therefore:

tan(phi_ij) = delta_h / d_ij

The slope is directional.

If j is higher than i:

phi_ij > 0

If j is lower than i:

phi_ij < 0

Therefore propagation uphill and downhill are not equivalent.


# 10. Current slope factor Ks

The intended base formulation discussed in the project is:

Ks(i,j) = exp(beta_s * tan(phi_ij))

However, the CURRENT code inherited an experimental offset:

Ks(i,j) =
    exp(
        beta_s *
        (tan(phi_ij) + c)
    )

with:

c = 3

In the modular implementation this is represented as:

slope_offset = 3.0

Current beta_s:

beta_s = 0.1

IMPORTANT:

The +3 offset is experimental, not a validated scientific constant.

Do not silently remove or change it, because experiments may depend on it.

If reviewing the physics, explicitly discuss whether the offset should exist
and compare it to the source formulation before modifying the code.


# 11. Wind representation

Earlier prototypes used ONE global wind speed and direction for the whole map.

That has now been replaced.

The current model uses a spatial wind vector field.

For every cell (x,y), the model stores:

wind_u[x,y]
wind_v[x,y]

where:

u = horizontal x wind component
v = vertical y wind component

From these we obtain:

V_w(x,y) = sqrt(u^2 + v^2)

theta_w(x,y) = atan2(v,u)


# 12. Synthetic wind field

The wind field is currently synthetic.

It contains:

- one prevailing/base wind direction,
- one base wind speed,
- several smooth spatial perturbations.

The perturbations use broad Gaussian regions so adjacent cells
receive similar wind values.

This is intentional.

Do NOT assign completely random independent wind speed/direction to each cell.

Current approximate configuration:

base wind speed:
    6 m/s

base wind direction:
    20 degrees

wind seed:
    20

maximum local speed variation:
    about +/- 2.5 m/s

maximum local direction variation:
    about +/- 30 degrees

The spatial wind field is currently FIXED in time.

Therefore the current model is:

V_w(x,y)
theta_w(x,y)

NOT yet:

V_w(x,y,t)
theta_w(x,y,t)

Spatiotemporal wind may be added later.


# 13. Wind on an edge i -> j

When calculating propagation between neighboring cells i and j,
do not directly average wind angles.

Instead average vector components:

u_ij = (u_i + u_j) / 2

v_ij = (v_i + v_j) / 2

Then:

V_w(i,j) = sqrt(u_ij^2 + v_ij^2)

theta_w(i,j) = atan2(v_ij, u_ij)

This avoids angle wrap-around problems.


# 14. Direction from i to j

The direction theta_ij is computed using the spatial displacement
from source cell i to target cell j.

Because matrix row indices increase downward,
geometry.py converts them to Cartesian orientation.

Conceptually:

dx = j_col - i_col
dy = i_row - j_row

theta_ij = atan2(dy, dx)


# 15. Current wind factor Kw

Current formulation:

Kw =
    exp(
        beta_w *
        V_w(i,j) *
        cos(theta_w(i,j) - theta_ij)
    )

Current beta_w:

beta_w = 0.1

Interpretation:

If wind points toward j:

cos(...) is positive
Kw > 1

If wind is opposite propagation:

cos(...) is negative
Kw < 1

If wind is perpendicular:

cos(...) ≈ 0
Kw ≈ 1


# 16. Moisture

Fuel moisture is implemented as a synthetic 2D spatial field:

M(x,y)

represented as a fuel-moisture fraction:

0.05 <= M <= 0.30

The moisture field is spatially smooth, generated using broad Gaussian features
without independent per-cell noise and without correlation to topography.

For each transition from burning cell i to unburned target cell j:

M_j = moisture[j_row, j_col]

Km(j) = exp(-beta_m * M_j)

Current prototype default:

beta_m = 3.0

IMPORTANT:
- beta_m is a temporary prototype value (not scientifically calibrated) and will
  be learned from data in future differentiable calibration stages.
- Because Km = exp(-beta_m * M_j) < 1 for all M_j > 0, P0 represents the
  zero-moisture baseline spread probability before wind, slope, and moisture adjustments.


# 17. Fuel

Fuel type and fuel properties have NOT yet been implemented
in the current Python prototype.

Ultimately P0 may depend on source and target fuel types:

P0[f_i, f_j]

Fuel information will also become important when Rothermel
is integrated.

Do not hard-code arbitrary fuel categories unless requested.


# 18. Rothermel integration - future goal

Rothermel is planned as the primary physical rate-of-spread component.

Long-term concept:

R_ij = directional Rothermel rate of spread

Then:

tau_ij = d_ij / max(R_ij, epsilon)

where:

tau_ij = travel time from i to j.

Wind, slope and moisture should eventually be incorporated
carefully into the physical ROS calculation.

Avoid double-counting wind/slope effects by applying the same physical
effect both inside Rothermel and again through independent multipliers.


# 19. Differentiable CA - long-term goal

A major research goal is to make the cellular automaton differentiable,
following ideas similar to PyTorchFire.

Eventually selected parameters should become trainable.

Candidates include:

beta_w
beta_s
moisture coefficients
fuel corrections
transition-model coefficients

Historical wildfire observations will serve as targets.

Instead of manually choosing all parameters,
the model should eventually minimize a loss function through
gradient-based optimization.


# 20. Proposed future differentiable transition

A previous architecture discussion proposed a transition kernel such as:

z_ij =
    beta_0
    + beta_fuel
    + beta_R * g(R_ij)
    + beta_d * d_ij
    + other corrections

Then:

p_ij = sigmoid(z_ij)

And aggregate neighboring ignition probability using:

p_ignite(j) =
    1 - product_i(
        1 - q_i * p_ij
    )

where q_i is the continuous burning probability/state of source cell i.

During differentiable training, probabilities should remain continuous
instead of sampling binary states at every step.


# 21. Future training concept

The future differentiable version may compare predicted fire spread
against historical wildfire observations.

Possible loss components previously discussed:

- BCE / probabilistic burn-map loss
- spatial/pooling loss
- arrival-time loss
- perimeter/boundary loss
- physics regularization

Possible optimizer:
Adam / AdamW

Initially, keep Rothermel physics fixed and train only a small number
of calibration/correction parameters.

Do NOT make every physical parameter trainable at once.


# 22. Current visualization

The visualization currently displays four panels:

1. Topography
2. Wind field
3. Fuel moisture map
4. Fire spread animation

Topography:
    terrain color map + elevation colorbar.

Wind:
    speed displayed as a scalar color map.
    direction shown with quiver/vector arrows.
    arrows are subsampled so the plot stays readable.

Fuel Moisture:
    moisture fraction displayed with YlGnBu colormap + colorbar.

Fire:
    green = not burning
    red = burning

The simulation is exported as a GIF.


# 23. Reproducibility

Topography and wind have separate seeds.

This is deliberate.

It allows repeated simulations on the exact same environmental conditions.

The stochastic wildfire process may use:

random_seed = None

so fire realizations vary between runs.

When conducting controlled experiments,
the fire seed can also be fixed.


# 24. Scientific development principles

When modifying this project:

1. Keep physical quantities and units explicit.
2. Do not introduce arbitrary constants without explaining them.
3. Distinguish temporary prototype assumptions from validated formulas.
4. Do not tune parameters merely until an animation "looks realistic."
5. Prefer parameters that can eventually be calibrated from historical data.
6. Keep environment generation separate from propagation physics.
7. Keep visualization separate from simulation logic.
8. Avoid duplicated calculations across files.
9. Prefer small pure functions for physical equations.
10. Preserve reproducibility using explicit random generators/seeds.


# 25. Architecture principles

Maintain modular separation.

terrain.py must not contain fire-spread logic.

wind.py must not decide whether cells ignite.

geometry.py should contain geometric calculations only.

simulation.py should contain propagation logic but not plotting.

visualization.py should never modify model state.

main.py should remain thin and primarily orchestrate components.

config.py should be the main place for adjustable parameters.


# 26. Immediate current architecture

The intended execution flow is:

config
   ↓
terrain generator ───────┐
                         │
wind generator ──────────┼──────┐
                         │      │
moisture generator ──────┤      │
                         ↓      │
                 simulation engine
                         │
                         ↓
                SimulationResult
                         │
                         ↓
                   visualization


Within one propagation edge:

burning cell i
      ↓
neighbor j
      ↓
theta_ij
      ↓
local wind Vw, theta_w
      ↓
Kw
      ↓
elevation difference
      ↓
phi_ij
      ↓
Ks
      ↓
target moisture M_j
      ↓
Km = exp(-beta_m * M_j)
      ↓
P_ij = P0 * Kw * Ks * Km
      ↓
combine all burning neighbors
      ↓
P_burn(j)
      ↓
stochastic ignition


# 27. Important distinction: current vs future

CURRENTLY IMPLEMENTED:

- 50x50 square grid
- 30 m cell size
- 8 neighbors
- synthetic complex topography
- fixed reproducible topography
- spatially heterogeneous smooth wind
- wind fixed over time
- spatially heterogeneous smooth fuel moisture
- moisture fixed over time
- slope-dependent Ks
- wind-dependent Kw
- moisture-dependent Km
- probabilistic ignition
- binary states 0/1
- edge clipping tracking
- 4-panel GIF visualization
- modular Python codebase


NOT YET IMPLEMENTED:

- real DEM input
- real meteorological wind data
- real fuel moisture / dynamic temporal moisture
- fuel maps
- Rothermel
- hexagonal grid
- 18-neighbor radius-2 hex interactions
- burned state
- differentiable PyTorch implementation
- trainable parameters
- historical wildfire calibration
- arrival-time modeling
- real wildfire validation


# 28. How to work with this codebase

Before implementing a requested change:

1. Inspect the relevant existing modules.
2. Preserve the modular architecture.
3. Identify which physical equation or model assumption is being changed.
4. Explain any new scientific assumption.
5. Avoid silently changing existing model behavior.
6. If a requested change affects multiple modules, update all affected files.
7. Run the project after edits and verify that:
   - imports work,
   - simulation runs,
   - output arrays have expected shapes,
   - probabilities remain valid,
   - visualization still works.

When I ask conceptual questions, explain the mathematics and physical meaning,
not only the Python implementation.

When I ask for code changes, edit the actual project files rather than
returning one giant replacement script unless I explicitly request that.