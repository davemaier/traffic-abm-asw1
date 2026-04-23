from dataclasses import dataclass
from typing import List
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

INITIAL_SPEED=20
CARS_TOTAL=10
TICKS=1000
TRACK_LENGTH=200
MAX_SPEED=50
ACCELERATION=0.5
DECELERATION=20
SAFE_DISTANCE=5

@dataclass
class Car:
    speed: float
    position: float
    next_car: 'Car'

    def step(self):
        self._adapt_speed()
        self._move()

    def _move(self):
        self.position = (self.position + self.speed / 10) % TRACK_LENGTH
    
    def _adapt_speed(self):
        """Adapt speed based on gap to next car"""

        gap = (self.next_car.position - self.position) % TRACK_LENGTH

        if self.speed < MAX_SPEED:
            self.speed += ACCELERATION
        
        # Brake hard if too close
        if gap < SAFE_DISTANCE:
            self.speed = max(0, self.speed - DECELERATION)



def main():
    cars:List[Car] = []

    for car in range(CARS_TOTAL):
        cars.append(Car(speed=INITIAL_SPEED, position=car, next_car=None))        

    for car_index in range(CARS_TOTAL):
        cars[car_index].next_car = cars[(car_index + 1) % CARS_TOTAL] 

    positions_over_time = []
    for tick in range(TICKS):
        for car in cars:
            car.step()
        positions_over_time.append([car.position for car in cars])
    

    # Visualization
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_rlim(0, 1.5)
    scat = ax.scatter([], [])
    
    def update(frame):
        pos = positions_over_time[frame]
        theta = 2 * np.pi * (np.array(pos) % TRACK_LENGTH) / TRACK_LENGTH
        r = np.ones_like(theta)
        scat.set_offsets(np.column_stack([theta, r]))
        return scat,
    
    anim = FuncAnimation(fig, update, frames=TICKS, interval=100, blit=True)
    plt.show()



if __name__ == "__main__":
    main()

  