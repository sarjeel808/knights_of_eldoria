class Hideout:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.capacity = 5  # Maximum hunters that can stay

    def can_enter(self, hunter) -> bool:
        return (
            hunter.x == self.x and
            hunter.y == self.y and
            not hunter.in_hideout
        )
