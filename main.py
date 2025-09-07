import tkinter as tk
from tkinter import ttk
import random
import logging
from grid import Grid
from hunter import Hunter
from knight import Knight
from hideout import Hideout
from treasure import Treasure

# Set up logging
logging.basicConfig(filename="eldoria_game_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

class EldoriaSimulation:
    def __init__(self, size=20):
        self.root = tk.Tk()
        self.root.title("Knights of Eldoria - Treasure Collector")

        # Game configuration
        self.game_speed = 500
        self.turn_count = 0
        self.paused = False
        self.cell_size = 30
        self.grid_size = size

        # Calculate window dimensions
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        self.window_height = self.canvas_height + 120  # Space for controls

        # Initialize UI and simulation
        self.setup_ui()
        self.setup_simulation()

        # Set window size and start the simulation
        self.root.geometry(f"{self.canvas_width}x{self.window_height}")
        self.root.after(self.game_speed, self.update)
        self.root.mainloop()

    def setup_ui(self):
        """Setup the user interface for the game"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Stats display
        self.stats_frame = tk.Frame(main_frame)
        self.stats_frame.pack(fill=tk.X, pady=5)

        self.score_label = tk.Label(self.stats_frame, text="Treasure Collected: 0%",
                                    font=("Arial", 12, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.hunter_labels = []
        for i in range(3):
            lbl = tk.Label(self.stats_frame, text=f"Hunter {i + 1}: 100%",
                           font=("Arial", 10), fg="cyan" if i == 0 else "blue")
            lbl.pack(side=tk.LEFT, padx=5)
            self.hunter_labels.append(lbl)

        # Game canvas
        self.canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # Control panel
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Speed control slider
        speed_frame = tk.Frame(control_frame)
        speed_frame.pack(side=tk.LEFT, expand=True)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_slider = ttk.Scale(speed_frame, from_=100, to_=1000,
                                      command=lambda v: setattr(self, 'game_speed', int(float(v))))
        self.speed_slider.set(self.game_speed)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Buttons
        button_frame = tk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        tk.Button(button_frame, text="Pause", command=self.toggle_pause).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Restart", command=self.restart).pack(side=tk.LEFT)

        # Key bindings
        self.root.bind("<Key>", self.handle_key)

    def setup_simulation(self):
        """Initialize the game state with grid, entities, and treasures"""
        self.grid = Grid(self.grid_size)
        self.turn_count = 0

        # Add hideouts
        for _ in range(3):
            x, y = self.grid.random_empty_cell()
            self.grid.add_hideout(Hideout(x, y))

        # Add hunters with different skills
        skills = ["navigation", "endurance", "stealth"]
        for i, skill in enumerate(skills):
            x, y = self.grid.random_empty_cell()
            hunter = Hunter(x, y, skill)
            if i == 0:  # The first hunter is the player
                hunter.is_player = True
            self.grid.add_hunter(hunter)

        # Add knights
        for _ in range(4):
            x, y = self.grid.random_empty_cell()
            self.grid.add_knight(Knight(x, y))

        # Add treasures
        for _ in range(15):
            x, y = self.grid.random_empty_cell()
            value = random.choice([3, 7, 13])
            self.grid.add_treasure(Treasure(x, y, value))

    def draw(self):
        """Render all game elements to the canvas"""
        self.canvas.delete("all")

        # Draw grid lines
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.canvas_height, fill="#f0f0f0")
            self.canvas.create_line(0, i * self.cell_size, self.canvas_width, i * self.cell_size, fill="#f0f0f0")

        # Draw all entities in the correct order
        self.draw_hideouts()
        self.draw_treasures()
        self.draw_knights()
        self.draw_hunters()

        # Display turn count
        self.canvas.create_text(10, 10, text=f"Turn: {self.turn_count}", font=("Arial", 10), anchor=tk.NW)

    def draw_hideouts(self):
        """Render hideouts on the grid"""
        for hideout in self.grid.hideouts:
            x1 = hideout.x * self.cell_size + 2
            y1 = hideout.y * self.cell_size + 2
            x2 = (hideout.x + 1) * self.cell_size - 2
            y2 = (hideout.y + 1) * self.cell_size - 2
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#4CAF50", outline="black", width=2)

    def draw_treasures(self):
        """Render treasures on the grid"""
        for treasure in self.grid.treasures:
            x = (treasure.x + 0.5) * self.cell_size
            y = (treasure.y + 0.5) * self.cell_size
            self.canvas.create_text(x, y, text="★", fill="#FFD700", font=("Arial", 18))
            self.canvas.create_text(x, y + 10, text=f"{treasure.value:.1f}%", fill="black", font=("Arial", 7))

    def draw_knights(self):
        """Render knights on the grid"""
        for knight in self.grid.knights:
            x = knight.x * self.cell_size
            y = knight.y * self.cell_size
            self.canvas.create_polygon(
                x + 5, y + 25, x + 15, y + 5, x + 25, y + 25,
                fill="#F44336", outline="black", width=2
            )

    def draw_hunters(self):
        """Render hunters on the grid"""
        for i, hunter in enumerate(self.grid.hunters):
            if hunter.in_hideout:
                fill = "#A5D6A7"  # Light green when in hideout
            elif hunter.collected_treasure:
                fill = "#FFF176"  # Yellow when carrying treasure
            else:
                fill = "#f0f0f0" if i == 0 else "#2196F3"  # Default colors for others

            outline = "red" if i == 0 else "black"
            x = hunter.x * self.cell_size
            y = hunter.y * self.cell_size

            # Draw hunter
            self.canvas.create_oval(
                x + 5, y + 5, x + self.cell_size - 5, y + self.cell_size - 5,
                fill=fill, outline=outline, width=3 if i == 0 else 1
            )

            # Hunter number and treasure info
            self.canvas.create_text(x + self.cell_size // 2, y + self.cell_size // 2, text=str(i + 1), fill="black", font=("Arial", 8, "bold"))
            if hunter.collected_treasure:
                self.canvas.create_text(
                    x + self.cell_size // 2, y, text=f"{hunter.collected_treasure.value:.1f}%",
                    fill="gold", font=("Arial", 8, "bold")
                )

    def update(self):
        """Update the game state each turn"""
        if not self.paused:
            self.turn_count += 1
            self.grid.update()
            self.draw()

            # Update UI
            self.score_label.config(text=f"Treasure Collected: {self.grid.collected_treasure_value:.1f}%")
            for i, hunter in enumerate(self.grid.hunters):
                status = f"Hunter {i + 1}: {hunter.stamina:.1f}%"
                if hunter.collected_treasure:
                    status += f" (Carrying: {hunter.collected_treasure.value:.1f}%)"
                self.hunter_labels[i].config(text=status)

            logging.info(f"Turn {self.turn_count}: Treasure collected: {self.grid.collected_treasure_value:.1f}%")
            for i, hunter in enumerate(self.grid.hunters):
                logging.info(f"Hunter {i + 1} - Stamina: {hunter.stamina:.1f}%")

            if not self.grid.is_simulation_over():
                self.root.after(self.game_speed, self.update)
            else:
                self.show_game_over()

    def handle_key(self, event):
        """Handle keyboard input to move the player"""
        if not self.grid.hunters or self.paused:
            return

        hunter = self.grid.hunters[0]  # Player hunter
        dx, dy = 0, 0

        if event.keysym == "Up":
            dy = -1
        elif event.keysym == "Down":
            dy = 1
        elif event.keysym == "Left":
            dx = -1
        elif event.keysym == "Right":
            dx = 1
        else:
            return

        # Handle knight collision and movement
        new_x = (hunter.x + dx) % self.grid.size
        new_y = (hunter.y + dy) % self.grid.size

        for knight in self.grid.knights:
            if knight.x == new_x and knight.y == new_y:
                hunter.stamina = max(0, hunter.stamina - 20)
                if hunter.collected_treasure:
                    # Drop treasure if hunter is carrying it
                    treasure = hunter.collected_treasure
                    treasure.x = hunter.x
                    treasure.y = hunter.y
                    self.grid.add_treasure(treasure)
                    hunter.collected_treasure = None
                logging.info(f"Hunter {hunter} collided with Knight at ({new_x}, {new_y}), stamina reduced")
                break

        # Move hunter and handle collection
        if hunter.move(self.grid, dx, dy):
            logging.info(f"Hunter {hunter} moved to ({hunter.x}, {hunter.y})")

    def toggle_pause(self):
        """Pause or resume the game"""
        self.paused = not self.paused
        logging.info(f"Game {'paused' if self.paused else 'resumed'}")

    def restart(self):
        """Restart the game"""
        logging.info("Game restarted.")
        self.grid.reset()
        self.setup_simulation()

    def show_game_over(self):
        """Display a game over message"""
        logging.info(f"Game Over! Total treasure collected: {self.grid.collected_treasure_value:.1f}%")
        self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2,
                               text="Game Over!", fill="red", font=("Arial", 24, "bold"))

# Run the simulation
EldoriaSimulation()
