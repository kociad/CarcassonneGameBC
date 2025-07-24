import pygame
import logging

from models.figure import Figure

import settings

logger = logging.getLogger(__name__)

class Player:
    
    def __init__(self, name, index, color, isAI=False, isHuman=False):
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
        self.isHuman = isHuman
        
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
        
    def setIsHuman(self, isHuman):
        self.isHuman = isHuman
        
    def serialize(self):
        return {
            "name": self.name,
            "score": self.score,
            "index": self.index,
            "color": self.color,
            "isAI": self.isAI,
            "figuresRemaining": len(self.figures),
            "isHuman": self.isHuman
        }
    
    @staticmethod
    def deserialize(data):
        try:
            name = str(data["name"])
            index = int(data["index"])
            color = str(data["color"])
            isAI = bool(data.get("isAI", False))
            score = int(data.get("score", 0))
            figuresRemaining = int(data.get("figuresRemaining", 7))
            isHuman = bool(data.get("isHuman", False))

            player = Player(name=name, index=index, color=color, isAI=isAI, isHuman=isHuman)
            player.score = score
            player.figures = [Figure(player) for _ in range(figuresRemaining)]

            return player

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to deserialize Player object: {e}\nData: {data}")
            return None
