import logging
import random
import typing

from models.player import Player

import settings

logger = logging.getLogger(__name__)

class AIPlayer(Player):
    """Represents an AI-controlled player."""
    def __init__(self, name: str, index: int, color: str, difficulty: str = 'medium') -> None:
        """Initialize an AIPlayer with a name, index, color, and difficulty level."""
        super().__init__(name, index, color, isAI=True)
        self.difficulty = difficulty
        logger.debug(f"AIPlayer initialized: name={name}, difficulty={difficulty}")

    def playTurn(self, gameSession: 'GameSession') -> None:
        """Perform the AI's turn logic."""
        logger.info(f"Player {self.name} is thinking...")
        logger.debug(f"AI difficulty: {self.difficulty}")
        currentCard = gameSession.getCurrentCard()
        placements = self._getAllValidPlacements(gameSession, currentCard)
        if not placements:
            logger.info(f"Player {self.name} couldn't place their card anywhere and discarded it")
            gameSession.skipCurrentAction()
            return
        scoredPlacements = []
        for (x, y, rotationsNeeded) in placements:
            originalRotation = currentCard.rotation
            for _ in range(rotationsNeeded):
                currentCard.rotate()
            gameSession.gameBoard.placeCard(currentCard, x, y)
            gameSession.detectStructures()
            score = self._evaluatePlacement(gameSession, x, y)
            scoredPlacements.append(((x, y, rotationsNeeded), score))
            gameSession.gameBoard.removeCard(x, y)
            while currentCard.rotation != originalRotation:
                currentCard.rotate()
        scoredPlacements.sort(key=lambda item: item[1], reverse=True)
        logger.debug(f"AI {self.name} scored placements: {scoredPlacements}")
        chosenPlacement = self._choosePlacementByDifficulty(scoredPlacements)
        logger.debug(f"AI {self.name} chose placement: {chosenPlacement}")
        x, y, rotationsNeeded = chosenPlacement
        for _ in range(rotationsNeeded):
            currentCard.rotate()
        if gameSession.playCard(x, y):
            gameSession.setTurnPhase(2)
            self._handleMeeplePlacement(gameSession, x, y)
        else:
            logger.error(f"Player {self.name} failed to place card at validated position [{x},{y}]")

    def _getAllValidPlacements(self, gameSession: 'GameSession', card: 'Card') -> list[tuple[int, int, int]]:
        """Return all valid (x, y, rotationsNeeded) placements for the current card."""
        placements = []
        candidatePositions = list(gameSession.getCandidatePositions())
        originalRotation = card.rotation
        for x, y in candidatePositions:
            for rotations in range(4):
                if gameSession.gameBoard.validateCardPlacement(card, x, y):
                    placements.append((x, y, rotations))
                card.rotate()
        while card.rotation != originalRotation:
            card.rotate()
        return placements

    def _evaluatePlacement(self, gameSession: 'GameSession', x: int, y: int) -> float:
        """Evaluate the score for placing a card at (x, y)."""
        score = 0
        for structure in gameSession.structures:
            if structure.getIsCompleted():
                score += structure.getScore(gameSession=gameSession)
        return score

    def _choosePlacementByDifficulty(self, scoredPlacements: list[tuple[tuple[int, int, int], float]]) -> tuple[int, int, int]:
        """Choose a card placement based on AI difficulty and scored placements."""
        if self.difficulty == 'hard':
            return scoredPlacements[0][0]
        elif self.difficulty == 'medium':
            if random.random() < 0.5:
                return scoredPlacements[0][0]
            else:
                return random.choice(scoredPlacements)[0]
        elif self.difficulty == 'easy':
            return random.choice(scoredPlacements)[0]
        else:
            return random.choice(scoredPlacements)[0]

    def _handleMeeplePlacement(self, gameSession: 'GameSession', targetX: int, targetY: int) -> None:
        """Handle the meeple placement phase for the AI using scoring and difficulty."""
        card = gameSession.lastPlacedCard
        terrains = card.getTerrains()
        possiblePositions = list(terrains.keys())
        validPlacements = []
        for direction in possiblePositions:
            structure = gameSession.structureMap.get((targetX, targetY, direction))
            if structure and not structure.getFigures() and self.figures:
                validPlacements.append(direction)
        scoredPlacements = []
        scoreSkip = 0
        for structure in gameSession.structures:
            if structure.getIsCompleted():
                scoreSkip += structure.getScore(gameSession=gameSession)
        scoredPlacements.append((None, scoreSkip))
        for direction in validPlacements:
            structure = gameSession.structureMap.get((targetX, targetY, direction))
            figure = self.getFigure()
            structure.addFigure(figure)
            score = 0
            for s in gameSession.structures:
                if s.getIsCompleted():
                    score += s.getScore(gameSession=gameSession)
            scoredPlacements.append((direction, score))
            structure.removeFigure(figure)
            self.addFigure(figure)
        scoringPlacements = [item for item in scoredPlacements if item[0] is not None and item[1] > 0]
        nonScoringPlacements = [item for item in scoredPlacements if item[0] is not None and item[1] == 0]
        scoredPlacements.sort(key=lambda item: item[1], reverse=True)
        logger.debug(f"AI {self.name} scored meeple placements: {scoredPlacements}")
        chosen = self._chooseMeeplePlacementByDifficulty(scoredPlacements, scoringPlacements, nonScoringPlacements)
        logger.debug(f"AI {self.name} chose meeple placement: {chosen}")
        if chosen is None:
            logger.info(f"Player {self.name} decided not to place a meeple")
            gameSession.skipCurrentAction()
            return
        if gameSession.playFigure(self, targetX, targetY, chosen):
            logger.info(f"Player {self.name} placed meeple on {chosen}")
            gameSession.nextTurn()
        else:
            logger.info(f"Player {self.name} couldn't place meeple on {chosen}")
            gameSession.skipCurrentAction()

    def _chooseMeeplePlacementByDifficulty(
        self,
        scoredPlacements: list[tuple[typing.Optional[str], float]],
        scoringPlacements: list[tuple[str, float]],
        nonScoringPlacements: list[tuple[str, float]]
    ) -> typing.Optional[str]:
        """Choose a meeple placement direction or None based on AI difficulty and scored placements."""
        if scoringPlacements:
            if self.difficulty == 'hard':
                return max(scoringPlacements, key=lambda item: item[1])[0]
            elif self.difficulty == 'medium':
                if random.random() < 0.5:
                    return max(scoringPlacements, key=lambda item: item[1])[0]
                else:
                    return None
            elif self.difficulty == 'easy':
                if random.random() < 0.1:
                    return max(scoringPlacements, key=lambda item: item[1])[0]
                else:
                    return None
            else:
                return None
        else:
            # No placements with immediate point gain
            return None