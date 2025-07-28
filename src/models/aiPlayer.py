import logging
import random
import typing
import time
from typing import List, Tuple, Optional, Dict, Any

from models.player import Player
from models.figure import Figure
from models.card import Card

import settings
from utils.settingsManager import settingsManager

logger = logging.getLogger(__name__)

class AIPreset:
    """Configuration presets for different AI difficulty levels."""
    
    EASY = {
        "completionBonus": 100,
        "sizeBonus": 20,
        "fieldMultiplier": 0.8,
        "conservationThreshold": 4,
        "placementThreshold": 20,
        "opponentBlocking": 0.5,
        "centerPenalty": 2.0,
        "meepleOpportunity": 80,
        "structureConnection": 15,
        "unoccupiedBonus": 25,
        "completionRatioBonuses": [30, 50, 70, 90],
        "sizePenalties": [0, 0, 0],
        "fieldBonuses": [10, 20, 30],
        "cityBonuses": [30, 50, 70],
        "roadBonuses": [25, 40, 55],
        "monasteryBonuses": [60, 90, 120]
    }
    
    NORMAL = {
        "completionBonus": 150,
        "sizeBonus": 30,
        "fieldMultiplier": 1.0,
        "conservationThreshold": 3,
        "placementThreshold": 15,
        "opponentBlocking": 0.7,
        "centerPenalty": 1.5,
        "meepleOpportunity": 120,
        "structureConnection": 20,
        "unoccupiedBonus": 35,
        "completionRatioBonuses": [40, 70, 100, 130],
        "sizePenalties": [0, 0, 0],
        "fieldBonuses": [15, 25, 35],
        "cityBonuses": [40, 60, 80],
        "roadBonuses": [30, 45, 60],
        "monasteryBonuses": [80, 120, 160]
    }
    
    HARD = {
        "completionBonus": 200,
        "sizeBonus": 40,
        "fieldMultiplier": 1.2,
        "conservationThreshold": 2,
        "placementThreshold": 10,
        "opponentBlocking": 0.9,
        "centerPenalty": 1.0,
        "meepleOpportunity": 150,
        "structureConnection": 25,
        "unoccupiedBonus": 45,
        "completionRatioBonuses": [50, 90, 130, 170],
        "sizePenalties": [0, 0, 0],
        "fieldBonuses": [20, 30, 40],
        "cityBonuses": [50, 70, 90],
        "roadBonuses": [35, 50, 65],
        "monasteryBonuses": [100, 150, 200]
    }
    
    EXPERT = {
        "completionBonus": 250,
        "sizeBonus": 50,
        "fieldMultiplier": 1.4,
        "conservationThreshold": 1,
        "placementThreshold": 5,
        "opponentBlocking": 1.0,
        "centerPenalty": 0.8,
        "meepleOpportunity": 180,
        "structureConnection": 30,
        "unoccupiedBonus": 55,
        "completionRatioBonuses": [60, 110, 160, 210],
        "sizePenalties": [0, 0, 0],
        "fieldBonuses": [25, 35, 45],
        "cityBonuses": [60, 80, 100],
        "roadBonuses": [40, 55, 70],
        "monasteryBonuses": [120, 180, 240]
    }

class AIPlayer(Player):
    """
    AI-controlled player with configurable difficulty presets.
    
    The AI uses a preset system to control its behavior and decision-making. Each preset
    contains various parameters that affect how the AI evaluates moves, prioritizes actions,
    and manages resources (meeples).
    
    Preset System:
    - EASY: Conservative play, focuses on simple completions, avoids complex strategies
    - NORMAL: Balanced approach, good mix of completion and expansion
    - HARD: Aggressive play, prioritizes quick completions and meeple liberation
    - EXPERT: Advanced strategies, sophisticated evaluation with multi-turn planning
    
    Key Preset Parameters:
    - completionBonus: Points awarded for completing structures (higher = more completion-focused)
    - sizeBonus: Points for larger structures (higher = prefers bigger structures)
    - fieldMultiplier: Multiplier for field scoring potential (higher = more field-focused)
    - conservationThreshold: When to conserve meeples (lower = more aggressive placement)
    - placementThreshold: Minimum score to place a meeple (higher = more selective)
    - opponentBlocking: Weight for blocking opponent moves (higher = more defensive)
    - centerPenalty: Penalty for placing near center (higher = avoids center)
    - meepleOpportunity: Bonus for meeple placement opportunities (higher = places more meeples)
    - structureConnection: Bonus for connecting to existing structures (higher = more connection-focused)
    - unoccupiedBonus: Bonus for unoccupied structures (higher = prefers empty structures)
    
    Structure-Specific Bonuses (arrays for different structure sizes):
    - roadBonuses: Points for roads of different sizes [small, medium, large]
    - cityBonuses: Points for cities of different sizes [small, medium, large]
    - monasteryBonuses: Points for monasteries based on completion proximity [near, mid, far]
    - fieldBonuses: Points for field control and potential [low, medium, high]
    
    Advanced Parameters:
    - sizePenalties: Penalties for structures that tie up meeples [small, medium, large]
    - completionRatioBonuses: Bonuses based on completion percentage [25%, 50%, 75%, 100%]
    
    The AI adapts its strategy based on game phase (early/mid/late) and uses these
    preset values to evaluate card placements, meeple placements, and overall game strategy.
    """
    
    def __init__(self, name: str, index: int, color: str, difficulty: str = "NORMAL") -> None:
        """
        Initialize an AI player.
        
        Args:
            name: The player's name
            index: The player's index in the game
            color: The player's color
            difficulty: AI difficulty level (EASY, NORMAL, HARD, EXPERT)
        """
        super().__init__(name, color, index, isAI=True)
        self._gamePhase = "early"
        self._lastScore = 0
        self._consecutiveLowScores = 0
        self._difficulty = difficulty.upper()
        self._preset = self._getPreset()

    def _getPreset(self) -> Dict[str, Any]:
        """Get the AI preset configuration for the current difficulty."""
        if self._difficulty == "EASY":
            return AIPreset.EASY
        elif self._difficulty == "HARD":
            return AIPreset.HARD
        elif self._difficulty == "EXPERT":
            return AIPreset.EXPERT
        else:
            return AIPreset.NORMAL

    def playTurn(self, gameSession: 'GameSession') -> None:
        """
        Perform the AI's turn logic with configurable strategy.
        
        The AI will either use simple placement logic or advanced simulation
        based on the AI_USE_SIMULATION setting.
        
        Args:
            gameSession: The current game session
        """
        logger.info(f"Player {self.name} is thinking...")
        delay = settingsManager.get("AI_TURN_DELAY", 1.0)
        time.sleep(delay)
        
        self._updateGamePhase(gameSession)
        
        if settingsManager.get("AI_USE_SIMULATION", False):
            self._playTurnWithAdvancedSimulation(gameSession)
        else:
            self._playTurnSimple(gameSession)

    def _updateGamePhase(self, gameSession: 'GameSession') -> None:
        """Update the current game phase based on cards played."""
        totalCards = len(gameSession.getCardsDeck()) + 1
        cardsPlayed = 71 - totalCards
        
        if cardsPlayed < 15:
            self._gamePhase = "early"
        elif cardsPlayed < 45:
            self._gamePhase = "mid"
        else:
            self._gamePhase = "late"

    def _playTurnSimple(self, gameSession: 'GameSession') -> None:
        """
        Execute simple AI logic without simulation.
        
        Uses random valid placement and basic meeple placement logic.
        
        Args:
            gameSession: The current game session
        """
        currentCard = gameSession.getCurrentCard()
        placement = gameSession.getRandomValidPlacement(currentCard)
        if not placement:
            logger.info(f"Player {self.name} couldn't place their card anywhere and discarded it")
            gameSession.skipCurrentAction()
            return
            
        x, y, rotationsNeeded = placement
        for _ in range(rotationsNeeded):
            currentCard.rotate()
            
        if gameSession.playCard(x, y):
            gameSession.setTurnPhase(2)
            self._handleMeeplePlacementSimple(gameSession, x, y)
        else:
            logger.error(f"Player {self.name} failed to place card at validated position [{x},{y}]")
            gameSession.skipCurrentAction()

    def _playTurnWithAdvancedSimulation(self, gameSession: 'GameSession') -> None:
        """
        Execute AI logic using advanced strategic evaluation and multi-turn simulation.
        
        Evaluates multiple placement options with lookahead and opponent analysis
        to choose the optimal move.
        
        Args:
            gameSession: The current game session
        """
        currentCard = gameSession.getCurrentCard()
        
        logger.debug(f"AI {self.name} starting advanced evaluation with card: {currentCard.imagePath}")
        
        possiblePlacements = self._getMultipleValidPlacements(gameSession, currentCard)
        if not possiblePlacements:
            logger.info(f"Player {self.name} couldn't place their card anywhere and discarded it")
            gameSession.skipCurrentAction()
            return
        
        logger.debug(f"AI {self.name} evaluating {len(possiblePlacements)} possible placements")
        
        strategicScores = []
        for i, placement in enumerate(possiblePlacements):
            x, y, rotationsNeeded, cardCopy = placement
            
            strategicScore = self._evaluateCardPlacementAdvanced(gameSession, x, y, cardCopy)
            strategicScore += self._evaluateMeepleOpportunityAdvanced(gameSession, x, y, cardCopy)
            strategicScore += self._evaluateOpponentBlocking(gameSession, x, y, cardCopy)
            strategicScore += self._evaluateMultiTurnPotential(gameSession, x, y, cardCopy)
            
            strategicScores.append((strategicScore, placement))
            logger.debug(f"AI {self.name} placement {i+1}: ({x},{y}) rotation {rotationsNeeded*90} strategic score: {strategicScore}")
        
        strategicScores.sort(reverse=True, key=lambda x: x[0])
        maxCandidates = settingsManager.get("AI_STRATEGIC_CANDIDATES", 5)
        if maxCandidates == -1:
            topCandidates = strategicScores
        else:
            topCandidates = strategicScores[:maxCandidates]
        
        logger.debug(f"AI {self.name} simulating top {len(topCandidates)} strategic candidates")
        
        bestCardMove = None
        bestCardScore = float('-inf')
        
        for strategicScore, placement in topCandidates:
            x, y, rotationsNeeded, cardCopy = placement
            
            cardScore = self._simulateCardPlacementAdvanced(gameSession, x, y, rotationsNeeded)
            
            logger.debug(f"AI {self.name} card simulation: ({x},{y}) rotation {rotationsNeeded*90} strategic={strategicScore}, card score={cardScore}")
            
            if cardScore > bestCardScore:
                bestCardScore = cardScore
                bestCardMove = placement
        
        if bestCardMove:
            x, y, rotationsNeeded, cardCopy = bestCardMove
            logger.debug(f"AI {self.name} chose best card placement: ({x},{y}) rotation {rotationsNeeded*90} score: {bestCardScore}")
            
            for _ in range(rotationsNeeded):
                currentCard.rotate()
            
            if gameSession.playCard(x, y):
                gameSession.setTurnPhase(2)
                self._handleMeeplePlacementAdvanced(gameSession, x, y)
            else:
                logger.error(f"Player {self.name} failed to place card at validated position [{x},{y}]")
                gameSession.skipCurrentAction()
        else:
            logger.info(f"Player {self.name} couldn't find any valid placements and will discard the card")
            gameSession.skipCurrentAction()

    def _getMultipleValidPlacements(self, gameSession: 'GameSession', card: Card) -> List[Tuple[int, int, int, Card]]:
        """
        Get all valid card placements using the game's existing validation.
        
        Args:
            gameSession: The current game session
            card: The card to find placements for
            
        Returns:
            List of tuples containing (x, y, rotation, cardCopy) for each valid placement
        """
        placements = []
        
        candidatePositions = gameSession.getCandidatePositions()
        logger.debug(f"AI {self.name} checking {len(candidatePositions)} candidate positions for card placement")
        
        originalRotation = card.rotation
        for x, y in candidatePositions:
            while card.rotation != originalRotation:
                card.rotate()
            
            for rotation in range(4):
                if gameSession.getGameBoard().validateCardPlacement(card, x, y):
                    cardCopy = self._createCardCopy(card)
                    for _ in range(rotation):
                        cardCopy.rotate()
                    placements.append((x, y, rotation, cardCopy))
                    logger.debug(f"AI {self.name} found valid placement at ({x},{y}) with rotation {rotation * 90}")
                card.rotate()
        
        while card.rotation != originalRotation:
            card.rotate()
        
        logger.debug(f"AI {self.name} found {len(placements)} valid placements")
        return placements

    def _createCardCopy(self, card: Card) -> Card:
        """
        Create a copy of a card for simulation.
        
        Args:
            card: The card to copy
            
        Returns:
            A new Card instance with the same properties
        """
        cardCopy = Card(
            imagePath=card.imagePath,
            terrains=card.terrains.copy(),
            connections=card.connections.copy() if card.connections else None,
            features=card.features.copy() if card.features else None
        )
        cardCopy.rotation = card.rotation
        return cardCopy

    def _simulateCardPlacementAdvanced(self, gameSession: 'GameSession', x: int, y: int, rotationsNeeded: int) -> float:
        """
        Simulate card placement using advanced strategic evaluation.
        
        Evaluates the potential score of placing a card at the given position
        considering structure completion, field potential, meeple opportunities,
        opponent blocking, and multi-turn potential.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            rotationsNeeded: Number of rotations needed for the card
            
        Returns:
            A score representing the desirability of this placement
        """
        currentCard = gameSession.getCurrentCard()
        originalRotation = currentCard.rotation
        
        for _ in range(rotationsNeeded):
            currentCard.rotate()
        
        score = self._evaluateCardPlacementAdvanced(gameSession, x, y, currentCard)
        score += self._evaluateMeepleOpportunityAdvanced(gameSession, x, y, currentCard)
        score += self._evaluateStructureCompletionPotential(gameSession, x, y, currentCard)
        score += self._evaluateFieldPotential(gameSession, x, y, currentCard)
        score += self._evaluateOpponentBlocking(gameSession, x, y, currentCard)
        score += self._evaluateMultiTurnPotential(gameSession, x, y, currentCard)
        
        while currentCard.rotation != originalRotation:
            currentCard.rotate()
        
        return score

    def _evaluateCardPlacementAdvanced(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """
        Evaluate the score of a card placement position using preset configuration.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            cardCopy: A copy of the card being evaluated
            
        Returns:
            A score representing the desirability of this placement
        """
        score = 0.0
        terrains = cardCopy.getTerrains()
        
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((x, y, direction))
            if structure:
                score += self._preset["structureConnection"]
                
                if structure.getIsCompleted():
                    score += self._preset["completionBonus"]
                    
                if not structure.getFigures():
                    score += self._preset["unoccupiedBonus"]
                
                totalSides = len(structure.cardSides)
                completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
                completionRatio = completedSides / totalSides if totalSides > 0 else 0
                
                # Apply completion ratio bonuses
                if completionRatio > 0.9:
                    score += self._preset["completionRatioBonuses"][3]
                elif completionRatio > 0.7:
                    score += self._preset["completionRatioBonuses"][2]
                elif completionRatio > 0.5:
                    score += self._preset["completionRatioBonuses"][1]
                elif completionRatio > 0.3:
                    score += self._preset["completionRatioBonuses"][0]
                
                # Apply size penalties
                if totalSides > 8:
                    score += self._preset["sizePenalties"][2]
                elif totalSides > 6:
                    score += self._preset["sizePenalties"][1]
                elif totalSides > 4:
                    score += self._preset["sizePenalties"][0]
                
                structureType = structure.getStructureType()
                if structureType == "City":
                    score += self._evaluateCitySpecific(gameSession, structure, completionRatio)
                elif structureType == "Road":
                    score += self._evaluateRoadSpecific(gameSession, structure, completionRatio)
                elif structureType == "Monastery":
                    score += self._evaluateMonasterySpecific(gameSession, structure, completionRatio)
        
        center = gameSession.getGameBoard().getCenter()
        distanceFromCenter = abs(x - center) + abs(y - center)
        score -= distanceFromCenter * self._preset["centerPenalty"]
        
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
            if not gameSession.structureMap.get((x, y, direction)):
                score += 10.0
        
        return score

    def _evaluateCitySpecific(self, gameSession: 'GameSession', structure: 'Structure', completionRatio: float) -> float:
        """Evaluate city-specific scoring potential using preset configuration."""
        score = 0.0
        
        totalSides = len(structure.cardSides)
        
        if completionRatio > 0.8:
            score += self._preset["cityBonuses"][2]
        elif completionRatio > 0.6:
            score += self._preset["cityBonuses"][1]
        elif completionRatio > 0.4:
            score += self._preset["cityBonuses"][0]
        
        if totalSides <= 4:
            score += 60.0
        elif totalSides <= 6:
            score += 40.0
        elif totalSides <= 8:
            score += 25.0
        
        return score

    def _evaluateRoadSpecific(self, gameSession: 'GameSession', structure: 'Structure', completionRatio: float) -> float:
        """Evaluate road-specific scoring potential using preset configuration."""
        score = 0.0
        
        totalSides = len(structure.cardSides)
        
        if completionRatio > 0.8:
            score += self._preset["roadBonuses"][2]
        elif completionRatio > 0.6:
            score += self._preset["roadBonuses"][1]
        elif completionRatio > 0.4:
            score += self._preset["roadBonuses"][0]
        
        if totalSides <= 3:
            score += 50.0
        elif totalSides <= 5:
            score += 35.0
        elif totalSides <= 7:
            score += 20.0
        
        return score

    def _evaluateMonasterySpecific(self, gameSession: 'GameSession', structure: 'Structure', completionRatio: float) -> float:
        """Evaluate monastery-specific scoring potential using preset configuration."""
        score = 0.0
        
        if completionRatio > 0.8:
            score += self._preset["monasteryBonuses"][2]
        elif completionRatio > 0.6:
            score += self._preset["monasteryBonuses"][1]
        elif completionRatio > 0.4:
            score += self._preset["monasteryBonuses"][0]
        
        return score

    def _evaluateMeepleOpportunityAdvanced(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """
        Evaluate potential meeple placement opportunities using preset configuration.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            cardCopy: A copy of the card being evaluated
            
        Returns:
            A score representing the potential for meeple placement
        """
        score = 0.0
        terrains = cardCopy.getTerrains()
        
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((x, y, direction))
            if structure and not structure.getFigures():
                if structure.getIsCompleted():
                    score += self._preset["completionBonus"] * 1.5
                else:
                    totalSides = len(structure.cardSides)
                    completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
                    completionRatio = completedSides / totalSides if totalSides > 0 else 0
                    score += completionRatio * self._preset["meepleOpportunity"]
                
                if len(self.figures) > 0:
                    score += 40.0
                else:
                    score += 5.0
                
                structureType = structure.getStructureType()
                if structureType == "Field":
                    score += self._evaluateFieldMeepleOpportunity(gameSession, structure)
        
        return score

    def _evaluateFieldMeepleOpportunity(self, gameSession: 'GameSession', structure: 'Structure') -> float:
        """Evaluate field meeple placement opportunities using preset configuration."""
        score = 0.0
        
        completedCities = [
            s for s in gameSession.structures
            if s.getStructureType() == "City" and s.getIsCompleted()
        ]
        
        touchedCities = set()
        for card, _ in structure.cardSides:
            neighbors = card.getNeighbors().values()
            touchedCards = set([card])
            touchedCards.update([n for n in neighbors if n])
            
            for cityStructure in completedCities:
                for cityCard, _ in cityStructure.cardSides:
                    if cityCard in touchedCards:
                        touchedCities.add(cityStructure)
                        break
        
        score += len(touchedCities) * 8.0
        
        fieldSize = len(structure.cardSides)
        if fieldSize > 8:
            score += self._preset["fieldBonuses"][2]
        elif fieldSize > 6:
            score += self._preset["fieldBonuses"][1]
        elif fieldSize > 4:
            score += self._preset["fieldBonuses"][0]
        
        return score

    def _evaluateOpponentBlocking(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """
        Evaluate the potential to block opponents or prevent them from scoring.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            cardCopy: A copy of the card being evaluated
            
        Returns:
            A score representing blocking potential
        """
        score = 0.0
        terrains = cardCopy.getTerrains()
        
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((x, y, direction))
            if structure:
                opponentFigures = [fig for fig in structure.getFigures() if fig.player != self]
                if opponentFigures:
                    totalSides = len(structure.cardSides)
                    completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
                    completionRatio = completedSides / totalSides if totalSides > 0 else 0
                    
                    blockingScore = 0
                    if completionRatio > 0.8:
                        blockingScore = 120.0
                    elif completionRatio > 0.6:
                        blockingScore = 80.0
                    elif completionRatio > 0.4:
                        blockingScore = 50.0
                    else:
                        blockingScore = 25.0
                    
                    score += blockingScore * self._preset["opponentBlocking"]
        
        return score

    def _evaluateMultiTurnPotential(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """
        Evaluate the potential for future turns and strategic positioning.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            cardCopy: A copy of the card being evaluated
            
        Returns:
            A score representing multi-turn potential
        """
        score = 0.0
        
        if self._gamePhase == "early":
            score += self._evaluateEarlyGamePositioning(gameSession, x, y, cardCopy)
        elif self._gamePhase == "mid":
            score += self._evaluateMidGamePositioning(gameSession, x, y, cardCopy)
        else:
            score += self._evaluateLateGamePositioning(gameSession, x, y, cardCopy)
        
        return score

    def _evaluateEarlyGamePositioning(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """Evaluate positioning for early game strategy."""
        score = 0.0
        
        center = gameSession.getGameBoard().getCenter()
        distanceFromCenter = abs(x - center) + abs(y - center)
        
        if distanceFromCenter <= 2:
            score += 35.0
        elif distanceFromCenter <= 4:
            score += 20.0
        elif distanceFromCenter <= 6:
            score += 10.0
        
        return score

    def _evaluateMidGamePositioning(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """Evaluate positioning for mid game strategy."""
        score = 0.0
        
        terrains = cardCopy.getTerrains()
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((x, y, direction))
            if structure and len(structure.cardSides) > 2:
                score += 25.0
        
        return score

    def _evaluateLateGamePositioning(self, gameSession: 'GameSession', x: int, y: int, cardCopy: Card) -> float:
        """Evaluate positioning for late game strategy."""
        score = 0.0
        
        terrains = cardCopy.getTerrains()
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((x, y, direction))
            if structure:
                totalSides = len(structure.cardSides)
                completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
                completionRatio = completedSides / totalSides if totalSides > 0 else 0
                
                if completionRatio > 0.8:
                    score += 70.0
                elif completionRatio > 0.6:
                    score += 40.0
        
        return score

    def _evaluateStructureCompletionPotential(self, gameSession: 'GameSession', x: int, y: int, card: Card) -> float:
        """
        Evaluate potential score gains from structure completion.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            card: The card being evaluated
            
        Returns:
            A score representing the potential for structure completion
        """
        score = 0.0
        terrains = card.getTerrains()
        
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((x, y, direction))
            if structure:
                totalSides = len(structure.cardSides)
                completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
                completionRatio = completedSides / totalSides if totalSides > 0 else 0
                
                if completionRatio > 0.8:
                    score += 100.0
                elif completionRatio > 0.6:
                    score += 70.0
                elif completionRatio > 0.4:
                    score += 45.0
                elif completionRatio > 0.2:
                    score += 25.0
                
                if not structure.getFigures():
                    score += 20.0
        
        return score

    def _evaluateFieldPotential(self, gameSession: 'GameSession', x: int, y: int, card: Card) -> float:
        """
        Evaluate potential score gains from field placement.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            card: The card being evaluated
            
        Returns:
            A score representing the potential for field scoring
        """
        score = 0.0
        terrains = card.getTerrains()
        
        for direction, terrainType in terrains.items():
            if direction == "C":
                continue
                
            if terrainType == "field":
                structure = gameSession.structureMap.get((x, y, direction))
                if structure:
                    completedCities = [
                        s for s in gameSession.structures
                        if s.getStructureType() == "City" and s.getIsCompleted()
                    ]
                    
                    touchedCities = set()
                    for card, _ in structure.cardSides:
                        neighbors = card.getNeighbors().values()
                        touchedCards = set([card])
                        touchedCards.update([n for n in neighbors if n])
                        
                        for cityStructure in completedCities:
                            for cityCard, _ in cityStructure.cardSides:
                                if cityCard in touchedCards:
                                    touchedCities.add(cityStructure)
                                    break
                    
                    fieldScore = len(touchedCities) * 6
                    score += fieldScore * self._preset["fieldMultiplier"]
                    
                    fieldSize = len(structure.cardSides)
                    if fieldSize > 8:
                        score += 35.0
                    elif fieldSize > 6:
                        score += 25.0
                    elif fieldSize > 4:
                        score += 15.0
                    elif fieldSize > 2:
                        score += 10.0
        
        return score

    def _shouldConserveMeeple(self, gameSession: 'GameSession') -> bool:
        """
        Determine if the AI should conserve meeples based on game state.
        
        Args:
            gameSession: The current game session
            
        Returns:
            True if the AI should conserve meeples, False otherwise
        """
        return len(self.figures) <= self._preset["conservationThreshold"]

    def _handleMeeplePlacementAdvanced(self, gameSession: 'GameSession', targetX: int, targetY: int) -> None:
        """
        Handle meeple placement using advanced strategic evaluation with preset configuration.
        
        Args:
            gameSession: The current game session
            targetX: X coordinate where the card was placed
            targetY: Y coordinate where the card was placed
        """
        card = gameSession.lastPlacedCard
        terrains = card.getTerrains()
        bestDirection = None
        bestScore = float('-inf')
        
        shouldConserve = self._shouldConserveMeeple(gameSession)
        
        for direction in terrains.keys():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((targetX, targetY, direction))
            if structure and not structure.getFigures() and len(self.figures) > 0:
                score = self._evaluateMeeplePlacementAdvanced(gameSession, targetX, targetY, direction)
                
                if structure.getIsCompleted():
                    score += self._preset["completionBonus"] * 1.5
                
                totalSides = len(structure.cardSides)
                completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
                completionRatio = completedSides / totalSides if totalSides > 0 else 0
                
                if completionRatio > 0.8:
                    score += 120.0
                elif completionRatio > 0.6:
                    score += 80.0
                elif completionRatio > 0.4:
                    score += 50.0
                elif completionRatio > 0.2:
                    score += 25.0
                
                if shouldConserve:
                    if not structure.getIsCompleted() and completionRatio < 0.5:
                        score *= 0.5
                    
                    if structure.getStructureType() == "Field":
                        score *= 0.7
                
                if score > bestScore:
                    bestScore = score
                    bestDirection = direction
        
        if bestDirection and bestScore > 0:
            threshold = self._preset["placementThreshold"] if shouldConserve else 0.0
            
            if bestScore >= threshold:
                if gameSession.playFigure(self, targetX, targetY, bestDirection):
                    logger.debug(f"Player {self.name} placed meeple on {bestDirection} (score: {bestScore}, conserving: {shouldConserve})")
                    # Check for completed structures and score them immediately
                    self._checkAndScoreCompletedStructures(gameSession)
                    gameSession.nextTurn()
                    return
            else:
                logger.debug(f"Player {self.name} chose not to place meeple (score: {bestScore} < threshold: {threshold}, conserving: {shouldConserve})")
        
        logger.info(f"Player {self.name} couldn't place meeple anywhere or chose not to")
        gameSession.skipCurrentAction()

    def _evaluateMeeplePlacementAdvanced(self, gameSession: 'GameSession', x: int, y: int, direction: str) -> float:
        """
        Evaluate the score of a meeple placement using preset configuration.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            direction: The direction to place the meeple
            
        Returns:
            A score representing the desirability of this meeple placement
        """
        score = 0.0
        structure = gameSession.structureMap.get((x, y, direction))
        
        if not structure:
            return 0.0
            
        if structure.getIsCompleted():
            score += self._preset["completionBonus"] * 1.5
        else:
            totalSides = len(structure.cardSides)
            completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
            completionRatio = completedSides / totalSides if totalSides > 0 else 0
            score += completionRatio * self._preset["meepleOpportunity"]
        
        if not structure.getFigures():
            score += 30.0
        
        structureType = structure.getStructureType()
        if structureType == "City":
            score += self._evaluateCityMeeplePlacement(structure)
        elif structureType == "Road":
            score += self._evaluateRoadMeeplePlacement(structure)
        elif structureType == "Monastery":
            score += self._evaluateMonasteryMeeplePlacement(structure)
        elif structureType == "Field":
            score += self._evaluateFieldMeeplePlacement(gameSession, structure)
            
        return score

    def _evaluateCityMeeplePlacement(self, structure: 'Structure') -> float:
        """Evaluate city meeple placement scoring."""
        score = 0.0
        
        totalSides = len(structure.cardSides)
        
        if totalSides <= 4:
            score += 60.0
        elif totalSides <= 6:
            score += 40.0
        elif totalSides <= 8:
            score += 25.0
        
        return score

    def _evaluateRoadMeeplePlacement(self, structure: 'Structure') -> float:
        """Evaluate road meeple placement scoring."""
        score = 0.0
        
        totalSides = len(structure.cardSides)
        
        if totalSides <= 3:
            score += 50.0
        elif totalSides <= 5:
            score += 35.0
        elif totalSides <= 7:
            score += 20.0
        
        return score

    def _evaluateMonasteryMeeplePlacement(self, structure: 'Structure') -> float:
        """Evaluate monastery meeple placement scoring."""
        score = 0.0
        
        totalSides = len(structure.cardSides)
        completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
        completionRatio = completedSides / totalSides if totalSides > 0 else 0
        
        if completionRatio > 0.6:
            score += 60.0
        elif completionRatio > 0.4:
            score += 40.0
        elif completionRatio > 0.2:
            score += 25.0
        
        return score

    def _evaluateFieldMeeplePlacement(self, gameSession: 'GameSession', structure: 'Structure') -> float:
        """Evaluate field meeple placement scoring."""
        score = 0.0
        
        completedCities = [
            s for s in gameSession.structures
            if s.getStructureType() == "City" and s.getIsCompleted()
        ]
        
        touchedCities = set()
        for card, _ in structure.cardSides:
            neighbors = card.getNeighbors().values()
            touchedCards = set([card])
            touchedCards.update([n for n in neighbors if n])
            
            for cityStructure in completedCities:
                for cityCard, _ in cityStructure.cardSides:
                    if cityCard in touchedCards:
                        touchedCities.add(cityStructure)
                        break
        
        score += len(touchedCities) * 8.0
        
        if len(structure.cardSides) > 8:
            score += 50.0
        elif len(structure.cardSides) > 6:
            score += 35.0
        elif len(structure.cardSides) > 4:
            score += 25.0
        
        return score

    def _handleMeeplePlacementSimple(self, gameSession: 'GameSession', targetX: int, targetY: int) -> None:
        """
        Handle meeple placement with simple logic.
        
        Args:
            gameSession: The current game session
            targetX: X coordinate where the card was placed
            targetY: Y coordinate where the card was placed
        """
        card = gameSession.lastPlacedCard
        terrains = card.getTerrains()
        bestDirection = None
        bestScore = float('-inf')
        
        for direction in terrains.keys():
            if direction == "C":
                continue
                
            structure = gameSession.structureMap.get((targetX, targetY, direction))
            if structure and not structure.getFigures():
                score = self._evaluateMeeplePlacement(gameSession, targetX, targetY, direction)
                if score > bestScore:
                    bestScore = score
                    bestDirection = direction
        
        if bestDirection and bestScore > 0:
            if gameSession.playFigure(self, targetX, targetY, bestDirection):
                logger.debug(f"Player {self.name} placed meeple on {bestDirection} (score: {bestScore})")
                # Check for completed structures and score them immediately
                self._checkAndScoreCompletedStructures(gameSession)
                gameSession.nextTurn()
                return
        
        logger.info(f"Player {self.name} couldn't place meeple anywhere or chose not to")
        gameSession.skipCurrentAction()

    def _checkAndScoreCompletedStructures(self, gameSession: 'GameSession') -> None:
        """Check for completed structures and score them immediately."""
        logger.debug("Checking completed structures...")
        for structure in gameSession.structures:
            structure.checkCompletion()
            if structure.getIsCompleted():
                logger.debug(f"Structure {structure.structureType} is completed!")
                gameSession.scoreStructure(structure)

    def _evaluateMeeplePlacement(self, gameSession: 'GameSession', x: int, y: int, direction: str) -> float:
        """
        Evaluate the score of a meeple placement.
        
        Args:
            gameSession: The current game session
            x: X coordinate for placement
            y: Y coordinate for placement
            direction: The direction to place the meeple
            
        Returns:
            A score representing the desirability of this meeple placement
        """
        score = 0.0
        structure = gameSession.structureMap.get((x, y, direction))
        
        if not structure:
            return 0.0
            
        if structure.getIsCompleted():
            score += 100.0
        else:
            totalSides = len(structure.cardSides)
            completedSides = sum(1 for card, _ in structure.cardSides if card.getPosition())
            completionRatio = completedSides / totalSides if totalSides > 0 else 0
            score += completionRatio * 50.0
        
        if not structure.getFigures():
            score += 30.0
            
        return score

    def _handleMeeplePlacement(self, gameSession: 'GameSession', targetX: int, targetY: int) -> None:
        """
        Handle the meeple placement phase for the AI using random logic.
        
        Args:
            gameSession: The current game session
            targetX: X coordinate where the card was placed
            targetY: Y coordinate where the card was placed
        """
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
                    # Check for completed structures and score them immediately
                    self._checkAndScoreCompletedStructures(gameSession)
                    gameSession.nextTurn()
                    return
                    
        logger.info(f"Player {self.name} couldn't place meeple anywhere")
        gameSession.skipCurrentAction()

    def serialize(self) -> dict:
        """
        Serialize the AI player to a dictionary.
        
        Returns:
            Dictionary containing serialized AI player data
        """
        baseData = super().serialize()
        baseData["difficulty"] = self._difficulty
        return baseData

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> Optional['AIPlayer']:
        """
        Deserialize an AI player from a dictionary.
        
        Args:
            data: Dictionary containing player data
            
        Returns:
            An AIPlayer instance if successful, None otherwise
        """
        try:
            name = str(data["name"])
            index = int(data["index"])
            color = str(data["color"])
            isAI = bool(data.get("isAI", True))
            score = int(data.get("score", 0))
            figuresRemaining = int(data.get("figuresRemaining", 7))
            isHuman = bool(data.get("isHuman", False))
            difficulty = str(data.get("difficulty", "NORMAL"))

            player = AIPlayer(name=name, index=index, color=color, difficulty=difficulty)
            player.score = score
            player.figures = [Figure(player) for _ in range(figuresRemaining)]
            logger.debug(f"Deserialized AI player {name} with {len(player.figures)} figures")
            return player
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to deserialize AIPlayer object: {e}\nData: {data}")
            return None