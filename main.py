# Phantom-jam demo: cars drive around a circular track with no obstacles,
# yet traffic jams still emerge spontaneously from driver behaviour alone.
# The model is a continuous-time cousin of the Nagel–Schreckenberg cellular
# automaton: each car accelerates, respects a minimum following distance, and
# occasionally dawdles. The randomness is the seed; the following rule is the
# amplifier that turns tiny speed dips into propagating stop-and-go waves.

import argparse
from dataclasses import dataclass
from datetime import datetime
import math
import random

import matplotlib.pyplot as plt
import pandas as pd

KMH_TO_MS = 1 / 3.6

# --- Scenario ----------------------------------------------------------------
CARS_TOTAL = 23                  # enough cars to sit in the "jam-prone" regime
TRACK_LENGTH = 230               # m — single-lane ring (no entries, no exits)
DEFAULT_MAX_SPEED = 30 * KMH_TO_MS  # 30 km/h in m/s — free-flow target speed

# --- Driver behaviour --------------------------------------------------------
SAFE_DISTANCE = 2.5              # m — if the gap to the car ahead falls below
                                 #     this, the driver slams the brakes
ACCELERATION = 1.0               # m/s² — gentle acceleration toward max_speed
SLOWDOWN_PROB = 0.3              # per second — chance per car of a random dawdle
SLOWDOWN_AMOUNT = 1.0            # m/s — size of one dawdle (driver-noise kick)

# --- Numerics / time ---------------------------------------------------------
TIME_STEP = 0.1                  # s — one model step, and one rendered frame
SIM_DURATION = 300               # s of simulated time
TICKS = int(SIM_DURATION / TIME_STEP)
RNG_SEED = 42                    # fix for reproducible experiments

# --- Visualisation -----------------------------------------------------------
PAUSE = 0.005                    # s between rendered frames

random.seed(RNG_SEED)


@dataclass
class Car:
    """A single vehicle driving around the ring.

    Cars form a linked list in ring order via ``next_car``: each car only
    knows the one immediately ahead, which is all it needs for the
    following rule. There is no explicit car length — ``SAFE_DISTANCE``
    plays that role (the minimum centre-to-centre separation).

    Attributes:
        position: Arc position along the ring, in metres, in [0, TRACK_LENGTH).
        next_car: The car immediately ahead on the ring.
        speed:    Current speed in m/s, in [0, max_speed].
    """

    position: float
    speed: float
    next_car: 'Car' = None

    def step(self, max_speed):
        """Advance this car by one simulation tick of length ``TIME_STEP``.

        A tick is: first decide a new speed based on the surroundings,
        then travel at that speed for the duration of the tick.
        """
        self._adapt_speed(max_speed)
        self._move()

    def _adapt_speed(self, max_speed):
        """Update ``self.speed`` using the three driver-behaviour rules.

        The rules are applied in order and can override each other:

        1. **Accelerate** gently toward ``max_speed``.
        2. **Brake** to zero if the gap to the car ahead is below
           ``SAFE_DISTANCE``. This is the mechanism that propagates jams
           upstream — one slow car forces the follower to brake, which
           forces *its* follower to brake, and so on.
        3. **Dawdle**: with a small probability, randomly lose a bit of
           speed. Represents driver inattention / imperfect control.

        The stochastic rule's probability is scaled by ``TIME_STEP`` so
        that the expected rate of dawdle events per second is invariant
        under changes to the integration step size.
        """
        gap = (self.next_car.position - self.position) % TRACK_LENGTH

        self.speed = min(max_speed, self.speed + ACCELERATION * TIME_STEP)

        if gap < SAFE_DISTANCE:
            self.speed = 0

        if random.random() < SLOWDOWN_PROB * TIME_STEP:
            self.speed = max(0, self.speed - SLOWDOWN_AMOUNT)

    def _move(self):
        """Advance ``self.position`` by ``speed * TIME_STEP``, wrapping around the ring."""
        self.position = (self.position + self.speed * TIME_STEP) % TRACK_LENGTH


def create_cars(max_speed):
    """Place cars evenly around the ring."""
    cars = [
        Car(position=TRACK_LENGTH / CARS_TOTAL * i, speed=max_speed / 2)
        for i in range(CARS_TOTAL)
    ]
    for i in range(CARS_TOTAL):
        cars[i].next_car = cars[(i + 1) % CARS_TOTAL]
    return cars


def average_speed(cars):
    return sum(car.speed for car in cars) / len(cars)


def run_simulation(max_speed, show_animation):
    """Run the simulation once, optionally with animation.

    Initial state: cars are spaced evenly around the ring and driving at
    half the maximum speed. Because spacing and speed are uniform, the
    system sits at an unstable equilibrium — any stochastic dawdle breaks
    the symmetry and a jam nucleates. Watch the ring for the first ~30 s
    of simulated time: you should see distinct clusters form and drift
    *backward* around the ring, even though every car is moving forward.
    """
    random.seed(RNG_SEED)

    # Place cars evenly around the ring. With uniform spacing and uniform speed
    # the system is in an unstable equilibrium — any random dawdle breaks it
    # and a jam nucleates. That's the whole point of the demo.
    cars = create_cars(max_speed)
    total_average_speed = 0

    if show_animation:
        # Ring-shaped plot: map each car's position (in metres) to an angle on a unit circle.
        _, ax = plt.subplots(figsize=(6, 6))
        ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, linewidth=2))
        ax.set_aspect("equal", "box")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.axis("off")
        scatter = ax.scatter([], [], s=40)
        plt.show(block=False)

    for tick in range(TICKS):
        # Advance every car by one TIME_STEP. Order within a tick matters a
        # little (sequential update), but not enough to change the qualitative story.
        for car in cars:
            car.step(max_speed)

        total_average_speed += average_speed(cars)

        if show_animation:
            angles = [2 * math.pi * c.position / TRACK_LENGTH for c in cars]
            scatter.set_offsets([(math.cos(a), math.sin(a)) for a in angles])
            plt.pause(PAUSE)

    return total_average_speed / TICKS


def sweep_max_speed(max_speeds):
    rows = []

    for max_speed in sorted(max_speeds):
        result = run_simulation(max_speed, show_animation=False)
        rows.append({
            "max_speed_m_per_s": max_speed,
            "average_speed_m_per_s": result,
        })

    results = pd.DataFrame(rows)

    print(results.round(2))

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results.to_csv(f"runs/max-speed-sweep-{timestamp}.csv", index=False)


def parse_args():
    parser = argparse.ArgumentParser(description="Run the phantom-jam demo.")
    parser.add_argument(
        "--max-speed",
        type=float,
        nargs="+",
        default=[DEFAULT_MAX_SPEED],
        help=(
            "one or more maximum speeds in m/s "
            f"(default: {round(DEFAULT_MAX_SPEED, 2)})"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if len(args.max_speed) == 1:
        run_simulation(args.max_speed[0], show_animation=True)
    else:
        sweep_max_speed(args.max_speed)


if __name__ == "__main__":
    main()
