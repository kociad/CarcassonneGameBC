import logging
import random
import typing
import copy

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
            logger.debug(f"AI {self.name}: Deep copying game session for card placement simulation at ({x}, {y}) with {rotationsNeeded} rotations.")
            simSession = copy.deepcopy(gameSession)
            simCard = simSession.getCurrentCard()
            for _ in range(rotationsNeeded):
                simCard.rotate()
            simSession.gameBoard.placeCard(simCard, x, y)
            simSession.detectStructures()
            completedGain = 0
            for structure in simSession.structures:
                if structure.getIsCompleted():
                    owners = structure.getMajorityOwners()
                    if any(owner.getIndex() == self.index for owner in owners):
                        completedGain += structure.getScore(gameSession=simSession)
            claimAndCompleteGain = 0
            for structure in simSession.structures:
                if structure.getIsCompleted() and not structure.getFigures() and self.figures:
                    figure = self.getFigure()
                    structure.addFigure(figure)
                    owners = structure.getMajorityOwners()
                    if any(owner.getIndex() == self.index for owner in owners):
                        claimAndCompleteGain = max(claimAndCompleteGain, structure.getScore(gameSession=simSession))
                    structure.removeFigure(figure)
                    self.addFigure(figure)
            potentialGain = 0
            for structure in simSession.structures:
                if not structure.getIsCompleted():
                    if any(f.getOwner().getIndex() == self.index for f in structure.getFigures()) or (not structure.getFigures() and self.figures):
                        potentialGain = max(potentialGain, structure.getScore(gameSession=simSession))
            if completedGain > 0:
                scoredPlacements.append(((x, y, rotationsNeeded), (3, completedGain)))
            elif claimAndCompleteGain > 0:
                scoredPlacements.append(((x, y, rotationsNeeded), (2, claimAndCompleteGain)))
            else:
                scoredPlacements.append(((x, y, rotationsNeeded), (1, potentialGain)))
        scoredPlacements.sort(key=lambda item: (item[1][0], item[1][1]), reverse=True)
        logger.debug(f"AI {self.name} scored placements: {scoredPlacements}")
        chosenPlacement = self._choosePlacementByDifficulty(scoredPlacements)
        logger.debug(f"AI {self.name} chose placement: {chosenPlacement}")
        x, y, rotationsNeeded = chosenPlacement
        for _ in range(rotationsNeeded):
            currentCard.rotate()
        if gameSession.playCard(x, y):
            gameSession.setTurnPhase(2)
            self._handleFigurePlacement(gameSession, x, y)
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

    def _choosePlacementByDifficulty(self, scoredPlacements: list[tuple[tuple[int, int, int], tuple[int, int]]]) -> tuple[int, int, int]:
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

    def _handleFigurePlacement(self, gameSession: 'GameSession', targetX: int, targetY: int) -> None:
        """Handle the figure placement phase for the AI using scoring and difficulty."""
        card = gameSession.lastPlacedCard
        terrains = card.getTerrains()
        possiblePositions = list(terrains.keys())
        validPlacements = []
        for direction in possiblePositions:
            structure = gameSession.structureMap.get((targetX, targetY, direction))
            if structure and not structure.getFigures() and self.figures:
                validPlacements.append(direction)
        scoredPlacements = []
        logger.debug(f"AI {self.name}: Deep copying game session for figure skip simulation at ({targetX}, {targetY}).")
        simSessionSkip = copy.deepcopy(gameSession)
        scoreSkip = 0
        for structure in simSessionSkip.structures:
            if structure.getIsCompleted():
                owners = structure.getMajorityOwners()
                if any(owner.getIndex() == self.index for owner in owners):
                    scoreSkip += structure.getScore(gameSession=simSessionSkip)
        scoredPlacements.append((None, scoreSkip))
        for direction in validPlacements:
            logger.debug(f"AI {self.name}: Deep copying game session for figure placement simulation at ({targetX}, {targetY}, {direction}).")
            simSession = copy.deepcopy(gameSession)
            simStructure = simSession.structureMap.get((targetX, targetY, direction))
            simPlayer = simSession.players[self.index]
            figure = simPlayer.getFigure()
            simStructure.addFigure(figure)
            score = 0
            for s in simSession.structures:
                if s.getIsCompleted():
                    owners = s.getMajorityOwners()
                    if any(owner.getIndex() == self.index for owner in owners):
                        score += s.getScore(gameSession=simSession)
            if not simStructure.getIsCompleted():
                score = max(score, simStructure.getScore(gameSession=simSession))
            scoredPlacements.append((direction, score))
        scoredPlacements.sort(key=lambda item: item[1], reverse=True)
        logger.debug(f"AI {self.name} scored figure placements: {scoredPlacements}")
        chosen = self._chooseFigurePlacementByDifficulty(scoredPlacements)
        logger.debug(f"AI {self.name} chose figure placement: {chosen}")
        if chosen is None:
            logger.info(f"Player {self.name} decided not to place a figure")
            gameSession.skipCurrentAction()
            return
        if gameSession.playFigure(self, targetX, targetY, chosen):
            logger.info(f"Player {self.name} placed figure on {chosen}")
            gameSession.nextTurn()
        else:
            logger.info(f"Player {self.name} couldn't place figure on {chosen}")
            gameSession.skipCurrentAction()

    def _chooseFigurePlacementByDifficulty(self, scoredPlacements: list[tuple[str | None, int]]) -> str | None:
        """Choose a figure placement direction or None based on AI difficulty and scored placements."""
        if not scoredPlacements:
            return None
        bestScore = scoredPlacements[0][1]
        minScoreThresholds = {
            'hard': 0,
            'medium': 0,
            'easy': 0
        }
        minScore = minScoreThresholds.get(self.difficulty, 0)
        if bestScore < minScore:
            if self.difficulty == 'hard':
                return None
            elif self.difficulty == 'medium':
                if random.random() < 0.2:
                    return scoredPlacements[0][0]
                else:
                    return None
            elif self.difficulty == 'easy':
                if random.random() < 0.5:
                    return scoredPlacements[0][0]
                else:
                    return None
            else:
                return None
        if self.difficulty == 'hard':
            return scoredPlacements[0][0]
        elif self.difficulty == 'medium':
            if random.random() < 0.5:
                return scoredPlacements[0][0]
            else:
                return None
        elif self.difficulty == 'easy':
            if random.random() < 0.1:
                return scoredPlacements[0][0]
            else:
                return None
        else:
            return scoredPlacements[0][0]