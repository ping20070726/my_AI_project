"""Pure game rules, independent of the desktop interface."""
import random

DIRECTIONS = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}


class Game:
    def __init__(self, width=28, height=22, rng=None):
        self.width, self.height = width, height
        self.rng = rng or random.Random()
        x, y = width // 2, height // 2
        self.snake = [(x, y), (x-1, y), (x-2, y)]
        self.direction = self.pending = (1, 0)
        self.turned = False
        self.score = 0
        self.over = self.won = False
        self.food = self.new_food()

    def new_food(self):
        free = [(x, y) for y in range(self.height) for x in range(self.width)
                if (x, y) not in self.snake]
        return self.rng.choice(free) if free else None

    def turn(self, name):
        direction = DIRECTIONS.get(name)
        if self.over or self.turned or not direction:
            return
        if direction != (-self.direction[0], -self.direction[1]) and direction != self.direction:
            self.pending = direction
            self.turned = True

    def step(self):
        if self.over:
            return 'over'
        self.direction = self.pending
        self.turned = False
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        eating = head == self.food
        body = self.snake if eating else self.snake[:-1]
        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height) or head in body:
            self.over = True
            return 'over'
        self.snake.insert(0, head)
        if eating:
            self.score += 10
            self.food = self.new_food()
            if self.food is None:
                self.over = self.won = True
                return 'win'
            return 'eat'
        self.snake.pop()
        return 'move'
