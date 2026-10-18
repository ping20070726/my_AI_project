"""Deterministic, UI-independent falling-block rules with a seven-piece bag."""
import random

SHAPES = {
    'I': ((0, 1), (1, 1), (2, 1), (3, 1)),
    'O': ((1, 0), (2, 0), (1, 1), (2, 1)),
    'T': ((1, 0), (0, 1), (1, 1), (2, 1)),
    'S': ((1, 0), (2, 0), (0, 1), (1, 1)),
    'Z': ((0, 0), (1, 0), (1, 1), (2, 1)),
    'J': ((0, 0), (0, 1), (1, 1), (2, 1)),
    'L': ((2, 0), (0, 1), (1, 1), (2, 1)),
}
COLORS = dict(zip(SHAPES, ('#51d6ef', '#ffd66b', '#b99aff', '#65dfad', '#ff7e95', '#719eff', '#ffa768')))
SPEEDS = {'简单': 800, '普通': 550, '困难': 330}


class Game:
    width, height = 10, 20

    def __init__(self, difficulty='普通', rng=None):
        self.rng = rng or random.Random()
        self.difficulty = difficulty
        self.board = [[None] * self.width for _ in range(self.height)]
        self.bag = []
        self.score = self.lines = 0
        self.over = False
        self.next_kind = self.draw()
        self.spawn()

    @property
    def level(self):
        return self.lines // 10 + 1

    @property
    def interval(self):
        return max(75, int(SPEEDS[self.difficulty] * .85 ** (self.level - 1)))

    def draw(self):
        if not self.bag:
            self.bag = list(SHAPES)
            self.rng.shuffle(self.bag)
        return self.bag.pop()

    def spawn(self):
        self.kind = self.next_kind
        self.next_kind = self.draw()
        self.shape = SHAPES[self.kind]
        self.x, self.y = 3, 0
        if not self.valid(self.shape, self.x, self.y):
            self.over = True

    def cells(self, shape=None, x=None, y=None):
        return [(a + (self.x if x is None else x), b + (self.y if y is None else y))
                for a, b in (self.shape if shape is None else shape)]

    def valid(self, shape, x, y):
        return all(0 <= a < self.width and 0 <= b < self.height and self.board[b][a] is None
                   for a, b in self.cells(shape, x, y))

    def move(self, dx, dy):
        if self.over or not self.valid(self.shape, self.x+dx, self.y+dy):
            return False
        self.x += dx
        self.y += dy
        return True

    def rotate(self, clockwise=True):
        if self.over or self.kind == 'O':
            return False
        size = 4 if self.kind == 'I' else 3
        rotated = tuple((size-1-b, a) if clockwise else (b, size-1-a) for a, b in self.shape)
        # Simple wall/floor kicks; intentionally not a full SRS implementation.
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1), (0, -2)):
            if self.valid(rotated, self.x+dx, self.y+dy):
                self.shape = rotated
                self.x += dx
                self.y += dy
                return True
        return False

    def ghost_y(self):
        y = self.y
        while self.valid(self.shape, self.x, y+1):
            y += 1
        return y

    def lock(self):
        if self.over:
            return 0
        for x, y in self.cells():
            self.board[y][x] = self.kind
        kept = [row for row in self.board if not all(row)]
        count = self.height - len(kept)
        self.score += (0, 100, 300, 500, 800)[count] * self.level
        self.lines += count
        self.board = [[None]*self.width for _ in range(count)] + kept
        self.spawn()
        return count

    def step(self, soft=False):
        if self.over:
            return None
        if self.move(0, 1):
            self.score += int(soft)
            return None
        return self.lock()

    def hard_drop(self):
        if self.over:
            return None
        target = self.ghost_y()
        self.score += 2 * (target-self.y)
        self.y = target
        return self.lock()
