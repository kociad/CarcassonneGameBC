import logging
import random
import typing
import time

from models.player import Player

import settings
from utils.settingsManager import settingsManager

logger = logging.getLogger(__name__)

class AIPlayer(Player):
    """Represents an AI-controlled player."""
    def __init__(self, name: str, index: int, color: str) -> None:
        super().__init__(name, index, color, isAI=True)

    def playTurn(self, gameSession: 'GameSession') -> None:
        """Perform the AI's turn logic."""
        logger.info(f"Player {self.name} is thinking...")
        delay = settingsManager.get("AI_TURN_DELAY", 1.0)
        time.sleep(delay)
        currentCard = gameSession.getCurrentCard()
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

    def _handleMeeplePlacement(self, gameSession: 'GameSession', targetX: int, targetY: int) -> None:
        """Handle the meeple placement phase for the AI."""
        if random.random() > 0.5:
            logger.debug(f"Player {self.name} decided not to place a meeple")
            gameSession.skipCurrentAction()
            return
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