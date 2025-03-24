from models.card import Card
from settings import GRID_SIZE

class GameBoard:
    """
    Represents the game board where cards are placed.
    """
    
    def __init__(self, gridSize=GRID_SIZE):
        """
        Initializes the game board with an empty grid.
        :param gridSize: The size of the board grid (default: 20x20).
        """
        self.gridSize = gridSize
        self.grid = [[None for _ in range(gridSize)] for _ in range(gridSize)]
        self.center = gridSize // 2
        
    def getGridSize(self):
        """
        gridSize getter method
        :return: A number representing the size of the square grid
        """
        return self.gridSize
    
    def getCenterPosition(self):
        """
        Returns the center position of the board.
        :return: Tuple (x, y) representing the center coordinates.
        """
        return self.center, self.center
    
    def placeCard(self, card, x, y):
        """
        Places a card on the board at the given coordinates without validation.
        :param card: The card (Card) to be placed.
        :param x: X-coordinate on the board.
        :param y: Y-coordinate on the board.
        """
        if not (0 <= x < GRID_SIZE):
            raise ValueError(f"x must be between 1 and {GRID_SIZE - 1}, got {x}")
        
        if not (0 <= y < GRID_SIZE):
            raise ValueError(f"y must be between 1 and {GRID_SIZE - 1}, got {y}")
            
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            self.grid[y][x] = card
            self.updateNeighbors(x,y)
    
    def getCard(self, x, y):
        """
        Retrieves a card from the board at the given coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :return: The card (Card) at the specified position, or None if empty.
        """
        if not (0 <= x < GRID_SIZE):
            raise ValueError(f"x must be between 1 and {GRID_SIZE - 1}, got {x}")
        
        if not (0 <= y < GRID_SIZE):
            raise ValueError(f"y must be between 1 and {GRID_SIZE - 1}, got {y}")
            
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            return self.grid[y][x]
            
        return None

    def validateCardPlacement(self, card, x, y):
        """
        Validates if a card can be placed on given space
        :param card: Card to be placed
        :param x: X-coordinate of selected space
        :param y: Y-coordinate of selected space
        :return: True if placement is valid, false otherwise
        """
        print("Validating card placement...")
        
        if not (0 <= x < GRID_SIZE) or not (0 <= y < GRID_SIZE):
            print(f"Placement invalid, coordinates out of bounds.")
            return False
        
        if self.getCard(x,y) is not None:
            print(f"Placement invalid, expected None in space, got {self.getCard(x,y)}")
            return False # Cannot place card where one already exists
            
        if not self.hasNeighbor(x,y):
            print(f"Placement invalid, no valid neighbor found")
            return False
            
        neighbors = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        
        for direction, (nx, ny) in neighbors.items():
            print(f"Testing terrains of neighbor {direction}...")
            if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize: # Validate only neighbors within the grid
                neighbor = self.getCard(nx, ny)
                if neighbor:
                    if card.getTerrains()[direction] != neighbor.getTerrains()[self.getOppositeDirection(direction)]:
                        print(f"Testing directions currentCard: {direction} X neighbor: {self.getOppositeDirection(direction)}")
                        print(f"Unable to place card, terrains don't match, testing currentcard: {card.getTerrains()[direction]} X neighbor: {neighbor.getTerrains()[self.getOppositeDirection(direction)]}")
                        return False  # Terrains do not match, placement is invalid
            
        return True  # Placement is valid
            
    def getOppositeDirection(self, direction):
        """
        Returns the opposite direction
        :param direction: Direction to which opposite will be returned
        :return: Opposite direction
        """
        opposites = {"N": "S", "E": "W", "S": "N", "W": "E"}
        return opposites[direction]
        
    def hasNeighbor(self, x, y):
        """
        Checks if selected space has an occupied neighbor
        :param x: X-coordinate of selected space
        :param y: Y-coordinate of selected space
        :return: True if space has a neighbor, false otherwise
        """
        print("Checking for neighbors...")
        
        neighbors = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        
        existsNeighbor = False # By default no neighbor is expected
        
        for direction, (nx, ny) in neighbors.items():
            print(f"Testing existence of neighbor {direction}...")
            if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize: # Validate only neighbors within the grid
                neighbor = self.getCard(nx, ny)
                if neighbor:
                    existsNeighbor = True
                    break

        return existsNeighbor
        
    def updateNeighbors(self, x, y):
        """
        Updates the neighbors dictionary for the card at (x, y)
        and also ensures reciprocal neighbor links are updated
        """
        card = self.getCard(x, y)
        if card is None:
            return

        directions = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }

        for direction, (nx, ny) in directions.items():
            neighbor = self.getCard(nx, ny)
            card.neighbors[direction] = neighbor
            if neighbor:
                opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
                neighbor.neighbors[opposite] = card
