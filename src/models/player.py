class Player:
    
    def __init__(self, name, index):
        """
        Initializes a player with a name, score, and a placeholder for figures.
        :param name: The name of the player.
        :param score: Current player score
        :param index: Players index in the game
        :figures: list of figures
        """
        self.name = name
        self.score = 0
        self.index = index
        self.figures = []  # Placeholder for figures (meeples), will be implemented later
    
    def addScore(self, points):
        """
        Adds points to the player's score.
        :param points: The number of points to add.
        """
        self.score += points