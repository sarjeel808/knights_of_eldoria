import unittest
import numpy as np
from hunter import Hunter
from treasure import Treasure
from knight import Knight
from grid import Grid
from hideout import Hideout
from a_star import a_star


class TestHunter(unittest.TestCase):
    def test_move_reduces_stamina(self):
        grid = Grid(5)
        hunter = Hunter(0, 0, "navigation")
        grid.add_hunter(hunter)
        hunter.move(grid, 1, 0)
        self.assertLess(hunter.stamina, 100.0)

    def test_collects_treasure(self):
        grid = Grid(5)
        treasure = Treasure(1, 0, 7)
        hunter = Hunter(0, 0, "stealth")
        grid.add_treasure(treasure)
        grid.add_hunter(hunter)
        hunter.move(grid, 1, 0)
        self.assertIsNotNone(hunter.collected_treasure)

    def test_hunter_enters_hideout_and_deposits(self):
        grid = Grid(5)
        hideout = Hideout(1, 0)
        hunter = Hunter(0, 0, "endurance")
        treasure = Treasure(0, 0, 13)
        hunter.collected_treasure = treasure
        grid.add_hideout(hideout)
        grid.add_hunter(hunter)
        hunter.move(grid, 1, 0)
        self.assertEqual(hunter.collected_treasure, None)
        self.assertGreater(grid.collected_treasure_value, 0)

    def test_skill_effects(self):
        grid = Grid(5)
        nav_hunter = Hunter(0, 0, "navigation")
        end_hunter = Hunter(0, 1, "endurance")
        stl_hunter = Hunter(0, 2, "stealth")
        nav_hunter.move(grid, 1, 0)
        end_hunter.move(grid, 1, 0)
        stl_hunter.move(grid, 1, 0)
        self.assertAlmostEqual(nav_hunter.stamina, 98.5, delta=0.1)
        self.assertAlmostEqual(end_hunter.stamina, 99.0, delta=0.1)
        self.assertAlmostEqual(stl_hunter.stamina, 98.2, delta=0.1)

    def test_hotspot_avoidance(self):
        grid = Grid(5)
        hunter = Hunter(0, 0, "endurance")
        grid.add_hunter(hunter)
        grid.knight_hotspots = [(2, 0)]
        hunter.take_action(grid)
        self.assertNotEqual(hunter.x, 1)


class TestTreasure(unittest.TestCase):
    def test_decay_reduces_value(self):
        t = Treasure(0, 0, 5)
        original = t.value
        t.decay()
        self.assertLess(t.value, original)

    def test_decay_removes_empty_treasure(self):
        t = Treasure(0, 0, 0.1)
        self.assertFalse(t.decay())


class TestKnight(unittest.TestCase):
    def test_energy_reduces_on_chase(self):
        grid = Grid(5)
        knight = Knight(0, 0)
        hunter = Hunter(2, 0, "navigation")
        grid.add_knight(knight)
        grid.add_hunter(hunter)
        knight.patrol(grid)
        self.assertLess(knight.energy, 100.0)

    def test_knight_restores_energy(self):
        knight = Knight(0, 0)
        knight.energy = 10.0
        knight._rest()
        self.assertEqual(knight.energy, 20.0)

    def test_hotspot_targeting(self):
        grid = Grid(5)
        knight = Knight(0, 0)
        grid.add_knight(knight)
        knight.grid = grid
        hunter1 = Hunter(1, 1, "endurance")
        hunter2 = Hunter(3, 3, "endurance")
        grid.add_hunter(hunter1)
        grid.add_hunter(hunter2)
        grid.knight_hotspots = [(3, 2)]
        target = knight._select_target(grid.hunters)
        self.assertEqual(target, hunter2)


class TestGameEnd(unittest.TestCase):
    def test_game_over_if_all_treasure_gone(self):
        grid = Grid(5)
        self.assertTrue(grid.is_simulation_over())

    def test_game_over_if_all_hunters_dead(self):
        grid = Grid(5)
        hunter = Hunter(0, 0, "stealth")
        hunter.stamina = 0
        hunter.down_steps = 4
        grid.add_hunter(hunter)
        self.assertTrue(grid.is_simulation_over())


class TestAStar(unittest.TestCase):
    def test_path_exists(self):
        grid = Grid(5)
        path = a_star((0, 0), (4, 4), grid)
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)

    def test_path_avoids_knight(self):
        grid = Grid(5)
        grid.add_knight(Knight(1, 0))
        path = a_star((0, 0), (4, 0), grid, avoid_knights=True)
        self.assertTrue(all((x, y) != (1, 0) for x, y in path))

    def test_path_avoids_hotspots(self):
        grid = Grid(5)
        grid.knight_hotspots = [(2, 2)]
        path = a_star((0, 0), (4, 4), grid, avoid_hotspots=True)
        self.assertTrue(all((x, y) != (2, 2) for x, y in path))


class TestMLIntegration(unittest.TestCase):
    def setUp(self):
        self.grid = Grid(5)
        for _ in range(3):
            self.grid.knights.append(Knight(0, 0))
        for _ in range(10):
            self.grid.knight_path_history.append([(i % 5, i % 5) for i in range(3)])

    def test_hotspot_prediction(self):
        self.grid.update_knight_hotspots()
        self.assertEqual(len(self.grid.knight_hotspots), 3)
        self.assertTrue(all(0 <= x < 5 and 0 <= y < 5 for (x, y) in self.grid.knight_hotspots))


if __name__ == '__main__':
    unittest.main()
