import logging
import random

from models.player import Player

import settings

logger = logging.getLogger(__name__)

class AIPlayer(Player):
    def __init__(self, name, index, color):
        super().__init__(name, index, color, isAI=True)

    def playTurn(self, gameSession):
        logger.info(f"{self.name} is thinking...")
        logger.debug(f"{self.name} (AI) is taking a turn...")

        candidatePositions = list(gameSession.getCandidatePositions())
        random.shuffle(candidatePositions)
        
        cardPlaced = False
        targetX, targetY = -1, -1
        currentCard = gameSession.getCurrentCard()

        # Try to place card
        for x, y in candidatePositions:
            for rotation in range(4):
                if gameSession.playCard(x, y):
                    cardPlaced = True
                    targetX, targetY = x, y
                    break
                currentCard.rotate()

            if cardPlaced:
                gameSession.setTurnPhase(2)
                break
                
        if not cardPlaced:
            logger.info(f"{self.name} cannot place card anywhere - discarding")
            gameSession.skipCurrentAction()
            return
            
        # Decide on meeple placement
        if random.random() > 0.5:
            logger.info(f"{self.name} decided not to place a meeple")
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
                    logger.info(f"{self.name} placed meeple on {direction}")
                    gameSession.nextTurn()
                    return
                    
        logger.info(f"{self.name} couldn't place meeple anywhere")
        gameSession.skipCurrentAction()
