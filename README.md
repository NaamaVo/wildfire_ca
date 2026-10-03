# Wildfire Cellular Automaton

All files should be in the same folder.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Structure

- `config.py` — parameters only (Grid, Terrain, Wind, Moisture, Fire, Output)
- `models.py` — shared data structures (WindField, SimulationDiagnostics, SimulationResult)
- `terrain.py` — topography generation
- `wind.py` — spatial wind-field generation
- `moisture.py` — spatial fuel-moisture field generation
- `geometry.py` — neighborhood, direction, and slope calculations
- `simulation.py` — fire-spread logic (Kw, Ks, Km, P_ij calculation and CA state updates)
- `visualization.py` — 4-panel maps, animation, GIF export
- `main.py` — orchestration only
