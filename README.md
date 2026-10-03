# Wildfire Cellular Automaton

A modular research prototype for physically informed stochastic wildfire propagation on spatial grids.

## Cell State Model

- **`0` = Not Burning / Unburned (Green)**: Fuel present and eligible for ignition.
- **`1` = Burning (Red)**: Actively spreading flame front. Each step, a burning cell remains burning with probability $P_{\text{continue}} = 0.3$, otherwise transitions to burned ($-1$).
- **`-1` = Burned (Brown)**: Extinguished / ash. Cannot ignite other cells and cannot reignite.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Project Structure

- `config.py` — parameters only (Grid, Terrain, Wind, Moisture, Fire, Output)
- `models.py` — shared data structures (WindField, SimulationDiagnostics, SimulationResult)
- `terrain.py` — synthetic topography generation
- `wind.py` — spatial vector wind-field generation
- `moisture.py` — spatial fuel-moisture field generation
- `geometry.py` — neighborhood, direction, and slope calculations
- `simulation.py` — 3-state CA propagation and burnout logic (Kw, Ks, Km, P_ij, Pcontinue)
- `visualization.py` — 4-panel maps, animation, and GIF export
- `main.py` — orchestration only
