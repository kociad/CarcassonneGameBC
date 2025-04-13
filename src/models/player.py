import pygame

from models.figure import Figure

class Player:
    
    def __init__(self, name, index, color):
        """
        Initializes a player with a name, score, and a placeholder for figures.
        :param name: The name of the player.
        :param score: Current player score
        :param index: Players index in the game
        :param figures: list of figures
        :param color: Color of players figures
        """
        self.name = name
        self.color = color
        self.score = 0
        self.index = index
        self.figures = [Figure(self) for _ in range(7)]  # Each player starts with 7 figures
        self.isComputer = False # Currently unused
        
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
        
    def getColor(self):
        """
        Player color getter method
        :return: Color of the player figures
        """
        return self.color
        
    def getColorWithAlpha(self, alpha=150):
        color = pygame.Color(self.color)
        color.a = alpha
        return (color)
        
    def getFigure(self):
        """
        Gets a figure rom the figures list
        :return: If the list contains any figures then figure, else False
        """
        print("Retrieving figure...")
        
        if self.figures:
            print("Figure retrieved")
            return self.figures.pop()
        print("Unable to retrieve figure")
        return False
        
    def addFigure(self, figure):
        """
        Add figure to the player's list
        :param figure: Figure to be added
        """
        self.figures.append(figure)
        
    
    def addScore(self, points):
        """
        Adds points to the player's score.
        :param points: The number of points to add.
        """
        self.score += points