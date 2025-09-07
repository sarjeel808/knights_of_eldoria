class Treasure:
    def __init__(self, x: int, y: int, value: float):
        self.x = x
        self.y = y
        self.value = value
        self.original_value = value

    def decay(self) -> bool:
        self.value = max(0, self.value - 0.1)
        return self.value > 0
