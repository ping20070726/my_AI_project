import tempfile
import unittest
from pathlib import Path
from engine import Game
from storage import load_scores, save_scores


class Rules(unittest.TestCase):
    def test_reverse_and_multiple_turns(self):
        g = Game()
        g.turn('Left')
        self.assertEqual(g.pending, (1, 0))
        g.turn('Up')
        g.turn('Left')
        self.assertEqual(g.pending, (0, -1))
        g.step()
        g.turn('Left')
        self.assertEqual(g.pending, (-1, 0))

    def test_growth(self):
        g = Game()
        x, y = g.snake[0]
        g.food = x+1, y
        self.assertEqual(g.step(), 'eat')
        self.assertEqual((g.score, len(g.snake)), (10, 4))
        self.assertNotIn(g.food, g.snake)

    def test_wall_and_frozen_game(self):
        g = Game()
        g.snake = [(27, 10), (26, 10), (25, 10)]
        self.assertEqual(g.step(), 'over')
        old = g.snake.copy()
        g.step()
        self.assertEqual(old, g.snake)

    def test_body_collision(self):
        g = Game()
        g.snake = [(3, 3), (3, 4), (4, 4), (4, 3), (5, 3)]
        self.assertEqual(g.step(), 'over')

    def test_tail_can_vacate(self):
        g = Game()
        g.snake = [(3, 3), (3, 4), (4, 4), (4, 3)]
        g.food = (10, 10)
        self.assertEqual(g.step(), 'move')
        self.assertFalse(g.over)

    def test_full_board_win(self):
        g = Game(3, 2)
        g.snake = [(1, 0), (0, 0), (0, 1), (1, 1), (2, 1)]
        g.food = (2, 0)
        self.assertEqual(g.step(), 'win')
        self.assertTrue(g.won)
        self.assertIsNone(g.food)

    def test_storage_round_trip_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'nested/scores.json'
            self.assertEqual(load_scores(path), {})
            save_scores(path, {'简单': 30, '普通': 10})
            self.assertEqual(load_scores(path), {'简单': 30, '普通': 10})
            for content in ('broken', '[]', 'null', '{"简单":true,"普通":-1}'):
                path.write_text(content)
                self.assertEqual(load_scores(path), {})


if __name__ == '__main__':
    unittest.main()
