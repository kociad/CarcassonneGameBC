import logging
import random

from models.player import Player

import settings

logger = logging.getLogger(__name__)

class AIPlayer(Player):
    def __init__(self, name, index, color):
        super().__init__(name, index, color, isAI=True)

    def playTurn(self, gameSession):
        logger.info(f"Player {self.name} is thinking...")
        #logger.debug(f"{self.name} (AI) is taking a turn...")

        currentCard = gameSession.getCurrentCard()
        
        # Try to find valid placement
        placement = gameSession.getRandomValidPlacement(currentCard)
        
        if not placement:
            logger.info(f"Player {self.name} couldn't place their card anywhere and discarded it")
            gameSession.skipCurrentAction()
            return
        
        x, y, rotations_needed = placement
        
        for _ in range(rotations_needed):
            currentCard.rotate()
        
        if gameSession.playCard(x, y):
            gameSession.setTurnPhase(2)
            self._handleMeeplePlacement(gameSession, x, y)
        else:
            logger.error(f"Player {self.name} failed to place card at validated position [{x},{y}]")

    def _handleMeeplePlacement(self, gameSession, targetX, targetY):
        """Handle meeple placement phase"""
        # Decide on meeple placement (50% chance)
        if random.random() > 0.5:
            logger.debug(f"Player {self.name} decided not to place a meeple")
            gameSession.skipCurrentAction()
            return
            
        # Try to place meeple
        card = gameSession.lastPlacedCard
        terrains = card.getTerrains()
        directions = list(terrains.keys())
        random.shuffle(directions)

        for direction in directions:
            structure = gameSession.structureMap.get((targetX, targetY, direction))
            
            if structure and not structure.getFigures():
                if gameSession.playFigure(self, targetX, targetY, direction):
                    logger.debug(f"Player {self.name} placed meeple on {direction}")
                    gameSession.nextTurn()
                    return
                    
        logger.info(f"Player {self.name} couldn't place meeple anywhere")
        gameSession.skipCurrentAction()