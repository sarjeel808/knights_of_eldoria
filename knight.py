from collections import defaultdict
import random
import math

class Knight:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.energy = 100.0
        self.hunter_heatmap = defaultdict(int)
        self.grid = None  # Reference to the game grid, set during patrol

    def patrol(self, grid):
        """Main patrol logic for the knight. Chooses to chase or retreat based on energy."""
        if self.grid is None:
            self.grid = grid  # Link knight to the grid once

        if self.energy <= 20.0:
            self._retreat_to_edge(grid)  # Low energy triggers retreat
        else:
            target = self._select_target(grid.hunters)
            if target:
                self._chase(target, grid)  # Pursue the selected hunter

    def _select_target(self, hunters):
        """
        Select a hunter to target using a combination of AI prediction
        and historical heatmap. Prefers hunters near predicted hotspots
        and those carrying treasure.
        """
        if not hunters:
            return None

        # Use AI hotspot prediction with 80% probability
        if (hasattr(self.grid, 'knight_hotspots') and
                self.grid.knight_hotspots and
                random.random() < 0.8):

            hotspot_hunters = [
                hunter for hunter in hunters
                if any(math.dist((hunter.x, hunter.y), hs) <= 5 for hs in self.grid.knight_hotspots)
            ]

            if hotspot_hunters:
                carrying = [h for h in hotspot_hunters if h.collected_treasure]
                return random.choice(carrying or hotspot_hunters)

        # Fallback: Use heatmap and prioritize treasure carriers
        return max(hunters,
                   key=lambda h: self.hunter_heatmap[(h.x, h.y)] + (10 if h.collected_treasure else 0))

    def _chase(self, target, grid):
        """
        Attempts to move closer to the target while avoiding hideouts.
        Reduces energy on successful movement and updates tracking heatmap.
        """
        moves = []
        if target.x != self.x:
            moves.append((1 if target.x > self.x else -1, 0))
        if target.y != self.y:
            moves.append((0, 1 if target.y > self.y else -1))

        random.shuffle(moves)  # Introduce movement variation

        for dx, dy in moves:
            new_x = (self.x + dx) % grid.size
            new_y = (self.y + dy) % grid.size

            # Avoid moving into a hideout
            if not any(h.x == new_x and h.y == new_y for h in grid.hideouts):
                self.x = new_x
                self.y = new_y
                self.energy = max(0, self.energy - 20.0)
                self.hunter_heatmap[(target.x, target.y)] += 1  # Update pursuit data
                break

    def _retreat_to_edge(self, grid):
        """
        Finds the closest grid edge not blocked by hideouts and moves there to rest.
        """
        edge_cells = []

        for y in range(grid.size):
            if not any(h.y == y for h in grid.hideouts):
                edge_cells.extend([(0, y), (grid.size - 1, y)])

        for x in range(grid.size):
            if not any(h.x == x for h in grid.hideouts):
                edge_cells.extend([(x, 0), (x, grid.size - 1)])

        if edge_cells:
            self.x, self.y = min(edge_cells, key=lambda pos: abs(pos[0] - self.x) + abs(pos[1] - self.y))

        self._rest()

    def _rest(self):
        """Restores knight’s energy when idle or at the edge."""
        self.energy = min(100.0, self.energy + 10.0)
