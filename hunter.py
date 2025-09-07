from typing import Optional
import random
import math
from a_star import a_star


class Hunter:
    def __init__(self, x: int, y: int, skill: str):
        self.x = x
        self.y = y
        self.skill = skill
        self.stamina = 100.0
        self.collected_treasure: Optional['Treasure'] = None
        self.is_player = False
        self.in_hideout = False
        self.memory_of_lost_treasure = None
        self.down_steps = 0

        self.known_treasures = []
        self.known_hideouts = []
        self.known_knights = []

        self.skill_effects = {
            'navigation': {'stamina_cost': 1.5, 'move_speed': 1.2},
            'endurance': {'stamina_cost': 1.0, 'move_speed': 1.0},
            'stealth': {'stamina_cost': 1.8, 'move_speed': 0.8}
        }

    def move(self, grid, dx=0, dy=0):
        new_x = (self.x + dx) % grid.size
        new_y = (self.y + dy) % grid.size

        if grid.is_cell_empty(new_x, new_y) or any(t.x == new_x and t.y == new_y for t in grid.treasures):
            stamina_cost = self.skill_effects[self.skill]['stamina_cost']
            self.stamina = max(0, self.stamina - stamina_cost)

            move_chance = self.skill_effects[self.skill]['move_speed']
            if random.random() < move_chance:
                self.x = new_x
                self.y = new_y

            self.collect_treasure(grid)

            self.in_hideout = any(h.x == self.x and h.y == self.y for h in grid.hideouts)
            if self.in_hideout and self.collected_treasure:
                grid.collected_treasure_value += self.collected_treasure.value
                self.collected_treasure = None

            for t in grid.treasures:
                if abs(t.x - self.x) <= 2 and abs(t.y - self.y) <= 2:
                    if (t.x, t.y) not in self.known_treasures:
                        self.known_treasures.append((t.x, t.y))

            for h in grid.hideouts:
                if abs(h.x - self.x) <= 2 and abs(h.y - self.y) <= 2:
                    if (h.x, h.y) not in self.known_hideouts:
                        self.known_hideouts.append((h.x, h.y))

            for k in grid.knights:
                if abs(k.x - self.x) <= 2 and abs(k.y - self.y) <= 2:
                    if (k.x, k.y) not in self.known_knights:
                        self.known_knights.append((k.x, k.y))

            return True
        return False

    def collect_treasure(self, grid):
        if self.collected_treasure is None:
            for treasure in grid.treasures[:]:
                if treasure.x == self.x and treasure.y == self.y:
                    self.collected_treasure = treasure
                    grid.treasures.remove(treasure)
                    break

    def take_action(self, grid):
        if self.is_player or self.in_hideout:
            return

        if hasattr(grid, 'knight_hotspots') and grid.knight_hotspots:
            for hotspot in grid.knight_hotspots:
                if math.dist((self.x, self.y), hotspot) < 5:
                    dx = 1 if self.x < hotspot[0] else -1
                    dy = 1 if self.y < hotspot[1] else -1
                    if self.move(grid, dx, dy):
                        return

        if not self.collected_treasure:
            visible_treasures = [
                t for t in grid.treasures
                if (t.x, t.y) in self.known_treasures and t.value > 0
            ]
            if visible_treasures:
                target = max(visible_treasures, key=lambda t: t.value)
                path = a_star((self.x, self.y), (target.x, target.y), grid)
                if path:
                    next_x, next_y = path[0]
                    self.move(grid, next_x - self.x, next_y - self.y)
                    return

        if self.collected_treasure:
            known_hideouts = [
                h for h in grid.hideouts
                if (h.x, h.y) in self.known_hideouts
            ]
            if known_hideouts:
                nearest = min(known_hideouts, key=lambda h: abs(h.x - self.x) + abs(h.y - self.y))
                path = a_star((self.x, self.y), (nearest.x, nearest.y), grid)
            else:
                path = []
        else:
            known_treasures = [
                t for t in grid.treasures
                if (t.x, t.y) in self.known_treasures and t.value > 0
            ]
            if known_treasures:
                nearest = min(known_treasures, key=lambda t: abs(t.x - self.x) + abs(t.y - self.y))
                path = a_star((self.x, self.y), (nearest.x, nearest.y), grid)
            else:
                path = []

        if path:
            next_x, next_y = path[0]
            self.move(grid, next_x - self.x, next_y - self.y)
        elif random.random() < 0.8:
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            self.move(grid, dx, dy)
