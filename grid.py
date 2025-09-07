from typing import List, Tuple
import random
from hunter import Hunter
from knight import Knight
from treasure import Treasure
from hideout import Hideout
from sklearn.cluster import KMeans
import numpy as np

class Grid:
    def __init__(self, size: int = 20):
        self.size = size
        self.hunters: List[Hunter] = []
        self.knights: List[Knight] = []
        self.treasures: List[Treasure] = []
        self.hideouts: List[Hideout] = []
        self.collected_treasure_value = 0
        self.knight_positions_history: List[Tuple[int, int]] = []
        self.knight_hotspots: List[Tuple[int, int]] = []

    def random_empty_cell(self) -> Tuple[int, int]:
        while True:
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.is_cell_empty(x, y):
                return x, y

    def is_cell_empty(self, x: int, y: int) -> bool:
        for h in self.hunters:
            if h.x == x and h.y == y and not h.in_hideout:
                return False
        for k in self.knights:
            if k.x == x and k.y == y:
                return False
        return True

    def add_hunter(self, hunter: Hunter):
        self.hunters.append(hunter)
        hunter.grid = self

    def add_knight(self, knight: Knight):
        self.knights.append(knight)
        knight.grid = self

    def add_treasure(self, treasure: Treasure):
        self.treasures.append(treasure)

    def add_hideout(self, hideout: Hideout):
        self.hideouts.append(hideout)

    def update_knight_hotspots(self):
        if len(self.knight_positions_history) >= 10:
            data = np.array(self.knight_positions_history[-50:])
            kmeans = KMeans(n_clusters=min(3, len(data)), random_state=42).fit(data)
            self.knight_hotspots = [tuple(map(int, center)) for center in kmeans.cluster_centers_]

    def update(self):
        for hunter in self.hunters[:]:
            if not hunter.is_player:
                hunter.take_action(self)

        self.knight_positions_history.extend((k.x, k.y) for k in self.knights)
        if len(self.knight_positions_history) > 100:
            self.knight_positions_history = self.knight_positions_history[-100:]

        self.update_knight_hotspots()

        for hunter in self.hunters[:]:
            if not hunter.is_player:
                hunter.take_action(self)

            if hunter.in_hideout:
                hunter.stamina = min(100, hunter.stamina + 1)
                if hunter.stamina >= 50:
                    hunter.in_hideout = False

            if hunter.stamina <= 0:
                hunter.down_steps += 1
                if hunter.down_steps > 3:
                    self.hunters.remove(hunter)
            else:
                hunter.down_steps = 0

        for knight in self.knights:
            knight.patrol(self)

        for hunter in self.hunters:
            for knight in self.knights:
                if (hunter.x == knight.x and hunter.y == knight.y and not hunter.in_hideout):
                    if random.random() < 0.5:
                        hunter.stamina = max(0, hunter.stamina - 5)
                    else:
                        hunter.stamina = max(0, hunter.stamina - 20)

                    if hunter.collected_treasure:
                        treasure = hunter.collected_treasure
                        treasure.x, treasure.y = hunter.x, hunter.y
                        self.add_treasure(treasure)
                        hunter.memory_of_lost_treasure = (treasure.x, treasure.y)
                        hunter.collected_treasure = None

        self.treasures = [t for t in self.treasures if t.decay()]

        for hideout in self.hideouts:
            hunters_in_hideout = [h for h in self.hunters
                                  if h.x == hideout.x and h.y == hideout.y and h.in_hideout]

            if len(hunters_in_hideout) < hideout.capacity:
                skill_set = {h.skill for h in hunters_in_hideout}
                if len(skill_set) >= 2 and random.random() < 0.2:
                    new_hunter = Hunter(hideout.x, hideout.y, random.choice(list(skill_set)))
                    self.add_hunter(new_hunter)

        for hideout in self.hideouts:
            resting_hunters = [h for h in self.hunters
                               if h.x == hideout.x and h.y == hideout.y and h.in_hideout]

            all_known = {
                'treasures': set(),
                'hideouts': set(),
                'knights': set()
            }

            for h in resting_hunters:
                all_known['treasures'].update(h.known_treasures)
                all_known['hideouts'].update(h.known_hideouts)
                all_known['knights'].update(h.known_knights)

            for h in resting_hunters:
                h.known_treasures = list(all_known['treasures'])
                h.known_hideouts = list(all_known['hideouts'])
                h.known_knights = list(all_known['knights'])

    def is_simulation_over(self) -> bool:
        return (len(self.treasures) == 0 or
                all(h.stamina <= 0 or h.down_steps > 3 for h in self.hunters))
