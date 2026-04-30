# traffic-abm

An agent-based model (ABM) exploring why and under which conditions **phantom traffic jams** emerge on a closed, single-lane road — the backward-travelling stop-and-go waves, spontaneous cluster formation, and stable jam clusters that appear even without any external obstacle.

## The model

Cars are arranged on a circular track. Each car is an autonomous agent that, on every tick:

1. Looks at the gap to the car ahead.
2. Accelerates gently if below its target speed.
3. Stops instantly (`v = 0`) if the gap drops below the safe distance.
4. Occasionally slows down at random — "human variability" — which is the seed of most phantom jams.

With enough cars and a stiff-enough braking response, those small local perturbations propagate backward around the loop and produce the characteristic phantom jam — no accident, no bottleneck, just emergent behaviour from the local rules.

The simulation renders live: a matplotlib window shows the ring of cars moving around a circle, updated each tick. It can also run a small parameter sweep over maximum speed.

## Parameters

Tunable at the top of [main.py](main.py). All quantities are in SI units (metres, seconds, m/s) unless noted.

| Name              | Meaning                                                            | Default              |
| ----------------- | ------------------------------------------------------------------ | -------------------- |
| `CARS_TOTAL`      | Number of vehicles on the ring                                     | 23                   |
| `TRACK_LENGTH`    | Circumference of the ring (m)                                      | 230                  |
| `DEFAULT_MAX_SPEED` | Default free-flow cap (m/s); cars start at `max_speed / 2`       | 30 km/h ≈ 8.33 m/s   |
| `ACCELERATION`    | Acceleration toward `max_speed` (m/s²)                             | 1.0                  |
| `SAFE_DISTANCE`   | Gap (m) below which a car brakes hard to `v = 0`                   | 2.5                  |
| `SLOWDOWN_PROB`   | Per-second probability a car dawdles (scaled by `TIME_STEP`)       | 0.3                  |
| `SLOWDOWN_AMOUNT` | Speed lost on one dawdle event (m/s)                               | 1.0                  |
| `TIME_STEP`       | Integration step (s); animation draws one frame per step           | 0.1                  |
| `SIM_DURATION`    | Total simulated time (s); `TICKS = SIM_DURATION / TIME_STEP`       | 300                  |
| `RNG_SEED`        | Seed for the stochastic slowdowns — same seed = reproducible run   | 42                   |
| `PAUSE`           | `plt.pause` between rendered frames (s)                            | 0.005                |

## Running it

This project uses [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
uv sync
uv run main.py
```

A matplotlib window opens with the live ring. Within ~30 s of simulated time you should see jam clusters nucleate and drift *backward* around the ring while every car continues to move forward — the signature of a phantom jam.

To run the animation with a different maximum speed, pass one value in m/s:

```bash
uv run main.py --max-speed 6
```

To sweep several maximum speeds, pass a list:

```bash
uv run main.py --max-speed 5 8.33 12
```

The sweep prints a table and saves the data as a timestamped CSV:

```text
   max_speed_m_per_s  average_speed_m_per_s
0               5.00                   3.80
1               8.33                   3.92
2              12.00                   3.77
```

The CSV filename is `max-speed-sweep-YYYY-MM-DD_HH-MM-SS.csv`.

## Background

See [docs/traffic_odd.md](docs/traffic_odd.md) for the ODD-style specification (purpose, entities, design concepts, initialisation, sub-models) the implementation is based on.
