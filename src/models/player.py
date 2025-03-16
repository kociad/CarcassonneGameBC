class Player:
    
    def __init__(self, name: str, index: int):
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
        
    def getName(self):
        """
        Player name getter method
        :return: Player name string
        """
        return self.name
        
    def getScore(self):
        """
        Player score getter method
        :return: Player score number
        """
        return self.score
        
    def getFigures(self):
        """
        Player figures getter method
        :return: List of figures held by the player
        """
        return self.figures
        
    def getIndex(self):
        """
        Player index getter method
        :return: Index of the player
        """
        return self.index
    
    def addScore(self, points: int):
        """
        Adds points to the player's score.
        :param points: The number of points to add.
        """
        self.score += points