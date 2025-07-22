import logging
import random

from models.player import Player

import settings

logger = logging.getLogger(__name__)

class AIPlayer(Player):
    def __init__(self, name, index, color):
        super().__init__(name, index, color, isAI=True)

    def playTurn(self, gameSession):
        logger.debug(f"{self.name} (AI) is taking a turn...")

        board = gameSession.getGameBoard()
        currentCard = gameSession.getCurrentCard()
        triedPositions = set()
        cardPlaced = False
        targetX, targetY = -1, -1

        # Použij sdílenou metodu pro získání kandidátských pozic
        candidatePositions = list(gameSession.getCandidatePositions())
        random.shuffle(candidatePositions)
        logger.debug(f"AI found {len(candidatePositions)} candidate positions")
        
        # Shuffle positions for randomness
        candidatePositions = list(candidatePositions)
        random.shuffle(candidatePositions)
        logger.debug(f"Shuffled {len(candidatePositions)} candidate positions")

        # 2. Try all candidate positions with all rotations
        for x, y in candidatePositions:
            logger.debug(f"Testing position {x};{y}...")
            for rotation in range(4):
                if (x, y, rotation) in triedPositions:
                    continue
                    
                logger.debug(f"Testing rotation {rotation}")
                triedPositions.add((x, y, rotation))

                if gameSession.playCard(x, y):
                    cardPlaced = True
                    targetX, targetY = x, y
                    rotationUsed = rotation
                    break

                currentCard.rotate()

            if cardPlaced:
                gameSession.setTurnPhase(2)
                break
                
        if not cardPlaced:
            logger.debug("AI could not place card anywhere. Discarding...")
            gameSession.skipCurrentAction()
            return
            
        # 3. Decide randomly whether to place a figure (e.g. 75% chance)
        if random.random() > 0.5:
            logger.debug("AI decided to skip figure placement randomly")
            gameSession.skipCurrentAction()
            return
            
        # 4. If placing, shuffle directions and try one by one
        card = gameSession.lastPlacedCard
        terrains = card.getTerrains()
        directions = list(terrains.keys())
        random.shuffle(directions)

        for direction in directions:
            terrainType = terrains[direction]
            
            """
            if terrainType not in ["city", "road", "monastery"]:
                continue  # Ignore fields for now
            """

            structure = gameSession.structureMap.get((targetX, targetY, direction))
            if structure and not structure.getFigures():
                if gameSession.playFigure(self, targetX, targetY, direction):
                    logger.debug(f"AI placed figure at ({targetX}, {targetY}) on {direction}")
                    gameSession.nextTurn()
                    return
                    
        logger.debug("AI skipped figure placement after testing all options")
        gameSession.skipCurrentAction()
