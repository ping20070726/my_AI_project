import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import Game, SHAPES
from storage import load_scores, save_scores


class Rules(unittest.TestCase):
    def test_seven_bag(self):
        g = Game(rng=random.Random(7))
        first = [g.kind, g.next_kind] + [g.draw() for _ in range(5)]
        self.assertEqual(set(first), set(SHAPES))

    def test_wall_and_floor(self):
        g = Game()
        while g.move(-1, 0):
            pass
        self.assertFalse(g.move(-1, 0))
        self.assertTrue(all(x >= 0 for x, y in g.cells()))
        while g.move(0, 1):
            pass
        self.assertFalse(g.move(0, 1))
        self.assertTrue(g.valid(g.shape, g.x, g.y))

    def test_rotation_cycle(self):
        g = Game()
        g.kind, g.shape, g.x, g.y = 'T', SHAPES['T'], 3, 5
        original = set(g.cells())
        for _ in range(4):
            self.assertTrue(g.rotate())
        self.assertEqual(set(g.cells()), original)
        g.rotate(False)
        g.rotate(True)
        self.assertEqual(set(g.cells()), original)

    def test_wall_kick(self):
        g = Game()
        g.kind, g.shape, g.x, g.y = 'I', ((2, 0), (2, 1), (2, 2), (2, 3)), -2, 5
        self.assertTrue(g.rotate())
        self.assertTrue(g.valid(g.shape, g.x, g.y))

    def test_failed_rotation_preserves_piece(self):
        g = Game()
        g.kind, g.shape, g.x, g.y = 'T', SHAPES['T'], 3, 5
        before = (g.shape, g.x, g.y)
        with patch.object(g, 'valid', return_value=False):
            self.assertFalse(g.rotate())
        self.assertEqual((g.shape, g.x, g.y), before)

    def test_hard_drop_and_preview(self):
        g = Game()
        preview, distance = g.next_kind, g.ghost_y()-g.y
        self.assertEqual(g.hard_drop(), 0)
        self.assertEqual(g.score, 2*distance)
        self.assertEqual(g.kind, preview)
        self.assertEqual(sum(bool(c) for row in g.board for c in row), 4)

    def test_four_lines(self):
        g = Game()
        g.board[-4:] = [['J']*9+[None] for _ in range(4)]
        g.kind, g.shape, g.x, g.y = 'I', ((0, 0), (0, 1), (0, 2), (0, 3)), 9, 16
        self.assertEqual(g.lock(), 4)
        self.assertEqual((g.score, g.lines), (800, 4))
        self.assertFalse(any(c for row in g.board for c in row))

    def test_line_compaction_and_level(self):
        g = Game()
        g.lines = 9
        g.board[18][0] = 'T'
        g.board[19] = ['J']*6 + [None]*4
        g.kind, g.shape, g.x, g.y = 'I', SHAPES['I'], 6, 18
        old_speed = g.interval
        self.assertEqual(g.lock(), 1)
        self.assertEqual(g.board[19][0], 'T')
        self.assertEqual((g.level, g.lines, g.score), (2, 10, 100))
        self.assertLess(g.interval, old_speed)

    def test_soft_drop_points(self):
        g = Game()
        g.step(soft=True)
        self.assertEqual(g.score, 1)

    def test_spawn_blocked_and_game_frozen(self):
        g = Game()
        g.board[0] = ['J']*10
        g.board[1] = ['J']*10
        g.spawn()
        self.assertTrue(g.over)
        score = g.score
        self.assertFalse(g.move(1, 0))
        self.assertFalse(g.rotate())
        self.assertIsNone(g.hard_drop())
        self.assertIsNone(g.step())
        self.assertEqual(g.score, score)

    def test_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/'nested/scores.json'
            self.assertEqual(load_scores(p), {})
            save_scores(p, {'普通': 100})
            self.assertEqual(load_scores(p), {'普通': 100})
            for text in ('broken', 'null', '[]', '{"普通":true,"困难":-1}'):
                p.write_text(text, encoding='utf-8')
                self.assertEqual(load_scores(p), {})
            p.write_bytes(b'\xff\xfe')
            self.assertEqual(load_scores(p), {})


if __name__ == '__main__':
    unittest.main()
