import time
from dataclasses import dataclass, field

DEFAULT_SPEED = 3.0  # units per second toward cliff
MAX_SPEED = 15.0
MIN_SPEED = -5.0
DRIFT_DELAY = 5.0  # seconds of no positive interaction before spiraling
DRIFT_RATE = 1.0  # units per second drift back toward DEFAULT_SPEED


@dataclass
class GameState:
    position: float = 0.0
    speed: float = DEFAULT_SPEED
    last_update: float = field(default_factory=time.time)
    last_interaction: float = field(default_factory=time.time)
    started: bool = False

    def tick(self) -> None:
        now = time.time()
        elapsed = now - self.last_update
        self.position = max(0.0, min(100.0, self.position + self.speed * elapsed))
        self.last_update = now
        if self.position > 5.0:
            self.started = True

        # after 5s of no interaction, drift speed back toward default
        if now - self.last_interaction > DRIFT_DELAY and self.speed < DEFAULT_SPEED:
            self.speed = min(DEFAULT_SPEED, self.speed + DRIFT_RATE * elapsed)

    def apply_effect(self, effect: float) -> None:
        """effect in [-1, 1]: positive = slow down, negative = speed up."""
        self.last_interaction = time.time()
        self.speed -= effect * 6.0
        self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed))

    def reset(self) -> None:
        self.position = 0.0
        self.speed = DEFAULT_SPEED
        self.last_update = time.time()
        self.last_interaction = time.time()
        self.started = False

    @property
    def game_over(self) -> bool:
        return self.position >= 100.0

    @property
    def won(self) -> bool:
        return self.started and self.position == 0.0


game = GameState()
