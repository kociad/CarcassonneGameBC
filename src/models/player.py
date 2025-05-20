import pygame
import logging

from models.figure import Figure
from settings import DEBUG

logger = logging.getLogger(__name__)

class Player:
    
    def __init__(self, name, index, color, isAI=False):
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
        self.isAI = isAI
        
    def getIsAI(self):
        """
        Is player AI getter method
        :return: True if player is AI controlled, False otherwise
        """
        #logger.debug(f"Player {self.name} AI status: {self.isAI}")
        return self.isAI
    
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
        logger.debug("Retrieving figure...")
        
        if self.figures:
            logger.debug("Figure retrieved")
            return self.figures.pop()
        logger.debug("Unable to retrieve figure")
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
        
    def serialize(self):
        return {
            "name": self.name,
            "score": self.score,
            "index": self.index,
            "color": self.color,
            "is_ai": self.isAI,
            "figures_remaining": len(self.figures)
        }
    
    @staticmethod
    def deserialize(data):
        from models.figure import Figure
        player = Player(
            name=data["name"],
            index=data["index"],
            color=data["color"],
            isAI=data.get("is_ai", False)
        )
        player.score = data["score"]
        player.figures = [Figure(player) for _ in range(data.get("figures_remaining", 7))]
        return player