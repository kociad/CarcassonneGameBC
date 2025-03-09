from models.card import Card

class GameBoard:
    """
    Represents the game board where tiles are placed.
    """
    
    def __init__(self, grid_size=20):
        """
        Initializes the game board with an empty grid.
        :param grid_size: The size of the board grid (default: 20x20).
        """
        self.grid_size = grid_size
        self.grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.center = grid_size // 2
    
    def get_center_position(self):
        """
        Returns the center position of the board.
        :return: Tuple (x, y) representing the center coordinates.
        """
        return self.center, self.center
    
    def place_tile(self, tile, x, y):
        """
        Places a tile on the board at the given coordinates without validation.
        :param tile: The tile (Card) to be placed.
        :param x: X-coordinate on the board.
        :param y: Y-coordinate on the board.
        """
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.grid[y][x] = tile
    
    def get_tile(self, x, y):
        """
        Retrieves a tile from the board at the given coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :return: The tile (Card) at the specified position, or None if empty.
        """
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[y][x]
        return None
