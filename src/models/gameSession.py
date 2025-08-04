import random
import logging
import typing
import utils.loggingConfig

from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from models.structure import Structure
from models.aiPlayer import AIPlayer
from models.figure import Figure
import settings
from utils.settingsManager import settingsManager
from models.cardSets.setLoader import loadAllCardSets, loadCardSet

logger = logging.getLogger(__name__)


class GameSession:
    """Manages the overall game state, including players, board, and card placement."""

    def __init__(self,
                 playerNames: list[str],
                 noInit: bool = False,
                 lobbyCompleted: bool = True,
                 networkMode: str = 'local') -> None:
        """Initialize a new game session."""
        self.players = []
        self.currentPlayer = None
        self.gameBoard = GameBoard()
        self.cardsDeck = []
        self.currentCard = None
        self.lastPlacedCard = None
        self.isFirstRound = True
        self.gameOver = False
        self.turnPhase = 1
        self.placedFigures = []
        self.structures = []
        self.structureMap = {}
        self.networkMode = networkMode
        self.lobbyCompleted = lobbyCompleted
        self.gameMode = None
        self.onTurnEnded = None
        self.onShowNotification = None
        self.onCommandExecuted = None

        self._candidatePositions = set()
        self._lastBoardState = None

        self._structureCache = {}
        self._structureCacheValid = False
        self._lastBoardHash = None

        self._validationCache = {}
        self._validationCacheValid = False

        self._neighborCache = {}
        self._neighborCacheValid = False

        if not noInit:
            self._generatePlayerList(playerNames)
            self.cardsDeck = self._generateCardsDeck()
            self._shuffleCardsDeck(self.cardsDeck)
            self._placeStartingCard()

    def getPlayers(self) -> list:
        """Return the list of player objects."""
        return self.players

    def getGameOver(self) -> bool:
        """Return True if the game is over."""
        return self.gameOver

    def getCurrentCard(self) -> typing.Any:
        """Return the currently drawn card."""
        return self.currentCard

    def getGameBoard(self) -> typing.Any:
        """Return the game board used by the current game session."""
        return self.gameBoard

    def getCardsDeck(self) -> typing.Any:
        """Return the cards deck assigned to the current game session."""
        return self.cardsDeck

    def getCurrentPlayer(self) -> typing.Any:
        """Return the player currently having their turn."""
        return self.currentPlayer

    def getPlacedFigures(self) -> list:
        """Return the list of figures placed on the board."""
        return self.placedFigures

    def getStructures(self) -> list:
        """Return the list of detected structures."""
        return self.structures

    def setTurnPhase(self, phase: int) -> None:
        """Set the current turn phase."""
        self.turnPhase = phase

    def getIsFirstRound(self) -> bool:
        """Return True if this is the first round."""
        return self.isFirstRound

    def _generatePlayerList(self, playerNames: list[str]) -> None:
        """Generate a list of indexed players for the game."""
        logger.debug("Generating a list of players...")
        colors = ["blue", "red", "green", "pink", "yellow", "black"]
        random.shuffle(colors)
        if playerNames:
            index = 0
            for player in playerNames:
                color = colors.pop()
                if player.startswith("AI_"):
                    difficulty = "NORMAL"
                    if player.startswith("AI_EASY_"):
                        difficulty = "EASY"
                    elif player.startswith("AI_HARD_"):
                        difficulty = "HARD"
                    elif player.startswith("AI_EXPERT_"):
                        difficulty = "EXPERT"
                    elif player.startswith("AI_NORMAL_"):
                        difficulty = "NORMAL"

                    self.players.append(
                        AIPlayer(player, index, color, difficulty))
                else:
                    self.players.append(Player(player, color, index))
                index += 1
            self.currentPlayer = self.players[len(self.players) - 1]
        logger.debug("Player list generated")

    def _generateCardsDeck(self) -> list:
        """Generate a deck of cards for the game by loading selected card sets."""
        logger.debug("Generating deck...")

        selectedCardSets = settingsManager.get("SELECTED_CARD_SETS",
                                               ["baseGame"])

        cardDefinitions = []
        cardDistributions = {}

        for setName in selectedCardSets:
            setData = loadCardSet(setName)
            if setData['definitions']:
                cardDefinitions.extend(setData['definitions'])
                cardDistributions.update(setData['distributions'])
                logger.info(
                    f"Loaded selected card set: {setName} with {len(setData['definitions'])} card definitions"
                )

        cards = []
        for card in cardDefinitions:
            image = card["image"]
            terrains = card["terrains"]
            connections = card["connections"]
            features = card["features"]
            count = cardDistributions.get(image, 1)
            cards.extend([
                Card(settings.TILE_IMAGES_PATH + image, terrains, connections,
                     features) for _ in range(count)
            ])

        logger.debug(
            f"Deck generated with {len(cards)} cards from {len(cardDefinitions)} card definitions"
        )
        return cards

    def _shuffleCardsDeck(self, deck: list) -> None:
        """Shuffle an existing deck of cards."""
        logger.debug("Shuffling deck...")
        random.shuffle(deck)
        logger.debug("Deck shuffled")

    def _placeStartingCard(self) -> None:
        """Place the first card automatically at the center of the board."""
        logger.debug("Playing first turn...")
        centerX, centerY = self.gameBoard.getCenterPosition()
        if self.cardsDeck:
            if self.playCard(centerX, centerY):
                self.isFirstRound = False
                logger.debug(
                    "First turn played - starting card placed, moving to next player"
                )
                self.nextTurn()
        else:
            logger.debug("Unable to play first round, no cardsDeck available")

    def _drawCard(self) -> typing.Any:
        """Draw a card from the deck for the current player."""
        logger.debug("Drawing card...")
        if self.cardsDeck:
            logger.debug("Card drawn")
            return self.cardsDeck.pop(0)
        return None

    def nextTurn(self) -> None:
        """Advance to the next player's turn."""
        if self.cardsDeck:
            logger.debug("Advancing player turn...")
            currentIndex = self.currentPlayer.getIndex()
            nextIndex = (currentIndex + 1) % len(self.players)
            for player in self.players:
                if player.getIndex() == nextIndex:
                    self.currentPlayer = player
                    break
            logger.info(
                f"{self.currentPlayer.getName()}'s turn (Player {self.currentPlayer.getIndex() + 1})"
            )
            self.currentCard = self._drawCard()
            if self.currentCard:
                logger.info(
                    f"New card drawn - {len(self.cardsDeck)} cards remaining")
                self.turnPhase = 1
                if self.onTurnEnded:
                    self.onTurnEnded()
            else:
                logger.debug("No card drawn, ending game")
                self.endGame()
        else:
            self.endGame()

    def playCard(self, x: int, y: int) -> bool:
        """Play the card placing part of the turn."""
        logger.debug("Playing card...")
        card = self.currentCard
        if not card:
            if not self.cardsDeck:
                logger.debug(
                    "Unable to play turn, no card is selected and no cardsDeck is available"
                )
                return False
            card = self._drawCard()
        if not self.gameBoard.validateCardPlacement(
                card, x, y) and not self.isFirstRound:
            logger.debug(
                f"Player {self.currentPlayer.getName()} was unable to place card, placement is invalid"
            )
            if self.onShowNotification and not self.currentPlayer.getIsAI():
                self.onShowNotification(
                    "error",
                    "Cannot place card here - terrain doesn't match adjacent cards!"
                )
            return False
        self.gameBoard.placeCard(card, x, y)
        self.lastPlacedCard = card
        self.currentCard = None
        if not self.isFirstRound:
            logger.info(
                f"Player {self.currentPlayer.getName()} placed a card at [{x - self.gameBoard.getCenter()},{self.gameBoard.getCenter() - y}]"
            )
        logger.debug(f"Last played card set to card {card} at {x};{y}")
        self._invalidateCandidateCache()
        self._invalidateStructureCache()
        self._invalidateValidationCache()
        self._invalidateNeighborCache()

        for player in self.players:
            if hasattr(player, 'invalidateEvaluationCache'):
                player.invalidateEvaluationCache()
            if hasattr(player, 'invalidateFigureCache'):
                player.invalidateFigureCache()

        if hasattr(self, 'onRenderCacheInvalidate'):
            self.onRenderCacheInvalidate()

        self.detectStructures()
        return True

    def discardCurrentCard(self) -> None:
        """Discard the currently selected card and select a new one."""
        if self.currentCard:
            self.currentCard = self._drawCard()

    def playAITurn(self, player: typing.Any = None) -> None:
        """If the current player is AI, trigger their turn."""
        if player is None:
            player = self.currentPlayer
        if isinstance(player, AIPlayer):
            player.playTurn(self)
            return

    def playTurn(self,
                 x: int,
                 y: int,
                 position: str = "C",
                 player: typing.Any = None) -> None:
        """Play a single complete game turn in two phases."""
        if player is None:
            player = self.currentPlayer

        logger.debug(
            f"playTurn called - Phase: {self.turnPhase}, Player: {player.getName()}, Position: ({x},{y})"
        )

        if self.turnPhase == 1:
            logger.debug("Turn Phase 1: Attempting to place card...")
            if self.playCard(x, y):
                self.turnPhase = 2
                logger.debug("Card placed successfully, moving to Phase 2")
            else:
                logger.debug("Card placement failed.")
            return
        elif self.turnPhase == 2:
            logger.debug("Turn Phase 2: Attempting to place figure...")
            figurePlaced = self.playFigure(player, x, y, position)
            if figurePlaced:
                logger.debug("Figure placed.")
                logger.debug("Checking completed structures...")
                for structure in self.structures:
                    structure.checkCompletion()
                    if structure.getIsCompleted():
                        logger.debug(
                            f"Structure {structure.structureType} is completed!"
                        )
                        self.scoreStructure(structure)
                self.nextTurn()
            else:
                logger.debug("Figure not placed or skipped.")

    def executeCommand(self, command) -> bool:
        """Execute a command received from the network."""
        try:
            logger.debug(
                f"Executing command {command.commandType} for player {command.playerIndex}"
            )

            if command.playerIndex != self.currentPlayer.getIndex():
                logger.warning(
                    f"Command from wrong player: {command.playerIndex} vs {self.currentPlayer.getIndex()}"
                )
                return False

            if command.commandType == "place_card":
                if self.currentCard:
                    while self.currentCard.rotation != command.cardRotation:
                        self.currentCard.rotate()
                success = self.playCard(command.x, command.y)
                if success:
                    self.turnPhase = 2
                return success

            elif command.commandType == "place_figure":
                if self.turnPhase != 2:
                    logger.warning("Cannot place figure in phase 1")
                    return False
                figurePlaced = self.playFigure(self.currentPlayer, command.x,
                                               command.y, command.position)
                if figurePlaced:
                    for structure in self.structures:
                        structure.checkCompletion()
                        if structure.getIsCompleted():
                            self.scoreStructure(structure)
                    self.nextTurn()
                return figurePlaced

            elif command.commandType == "skip_action":
                if command.actionType == "card" and self.turnPhase == 1:
                    self.skipCurrentAction()
                    return True
                elif command.actionType == "figure" and self.turnPhase == 2:
                    self.skipCurrentAction()
                    return True
                else:
                    logger.warning(
                        f"Cannot skip {command.actionType} in phase {self.turnPhase}"
                    )
                    return False

            elif command.commandType == "rotate_card":
                if self.currentCard and self.turnPhase == 1:
                    self.currentCard.rotate()
                    return True
                else:
                    logger.warning("Cannot rotate card")
                    return False

            else:
                logger.warning(f"Unknown command type: {command.commandType}")
                return False

        except Exception as e:
            logger.exception(
                f"Error executing command {command.commandType}: {e}")
            return False
        finally:
            if self.onCommandExecuted:
                self.onCommandExecuted(command)

    def skipCurrentAction(self) -> None:
        """Skip the current phase action with official rules validation."""
        if self.turnPhase == 1:
            logger.debug("Attempting to skip card placement...")
            if self.canPlaceCardAnywhere(self.currentCard):
                logger.debug(
                    f"Player {self.currentPlayer.getName()} was unable to skip card placement - card can be placed somewhere on the board"
                )
                if self.onShowNotification and not self.currentPlayer.getIsAI(
                ):
                    self.onShowNotification(
                        "warning",
                        "Cannot discard card - it can be placed on the board!")
            else:
                logger.info(
                    f"Player {self.currentPlayer.getName()} discarded card - no valid placement was found"
                )
                self.discardCurrentCard()
                if not self.cardsDeck:
                    self.endGame()
        elif self.turnPhase == 2:
            logger.info(
                f"Player {self.currentPlayer.getName()} skipped meeple placement"
            )
            logger.debug("Finalizing turn...")
            for structure in self.structures:
                structure.checkCompletion()
                if structure.getIsCompleted():
                    self.scoreStructure(structure)
            self.nextTurn()
            self.turnPhase = 1

    def playFigure(self, player: typing.Any, x: int, y: int,
                   position: str) -> bool:
        """Place a figure on a valid card position."""
        logger.debug("Playing figure...")
        card = self.gameBoard.getCard(x, y)
        if card != self.lastPlacedCard:
            logger.debug(
                f"Player {player.getName()} was unable to play figure on card {self.gameBoard.getCard(x,y)} at [{x},{y}], can only place figures on last played card"
            )
            if self.onShowNotification and not player.getIsAI():
                self.onShowNotification(
                    "error",
                    "Cannot place meeple here - only on the card you just placed!"
                )
            return False
        if not card:
            logger.debug(
                f"Player {player.getName()} was unable to place their meeple at [{x},{y}], no card was found."
            )
            if self.onShowNotification and not player.getIsAI():
                self.onShowNotification("error",
                                        "No card found at this position!")
            return False
        structure = self.structureMap.get((x, y, position))
        if structure:
            if structure.figures:
                logger.debug(
                    f"Player {player.getName()} was unable to place their meeple at [{x},{y}], position {position}, the structure is already occupied"
                )
                if self.onShowNotification and not player.getIsAI():
                    self.onShowNotification(
                        "error",
                        "Cannot place meeple - this structure is already occupied!"
                    )
                return False
        if player.figures:
            logger.debug(
                f"Player {player.getName()} has {len(player.figures)} figures before placement"
            )
            figure = player.getFigure()
            logger.debug(
                f"Player {player.getName()} has {len(player.figures)} figures after getFigure()"
            )
            if figure.place(card, position):
                self.placedFigures.append(figure)
                logger.info(
                    f"Player {player.getName()} placed a figure on {position} position at [{x - self.gameBoard.getCenter()},{self.gameBoard.getCenter() - y}]"
                )
                if structure:
                    structure.addFigure(figure)
                logger.debug(
                    f"Player {player.getName()} has {len(player.figures)} figures after successful placement"
                )
                logger.debug("Figure played")
                return True
            else:
                player.addFigure(figure)
                logger.debug(
                    f"Player {player.getName()} has {len(player.figures)} figures after failed placement (figure returned)"
                )
        logger.debug(
            f"Player {player.getName()} was unable to place their meeple, player has no meeples left"
        )
        if self.onShowNotification and not player.getIsAI():
            self.onShowNotification("error", "No meeples left to place!")
        return False

    def detectStructures(self) -> None:
        """Update structures based only on the last placed card."""
        logger.debug("Updating structures based on the last placed card...")
        if not self.lastPlacedCard:
            logger.debug("No card was placed. Skipping structure detection.")
            return

        currentBoardHash = self._getBoardStateHash()
        if (self._structureCacheValid
                and self._lastBoardHash == currentBoardHash
                and self._structureCache):
            logger.debug("Using cached structure detection results")
            return

        position = self.gameBoard.getCardPosition(self.lastPlacedCard)
        if not position:
            logger.debug("Last placed card position not found.")
            return

        x, y = position
        self.visited = set()

        for direction in self.lastPlacedCard.getTerrains().keys():
            cacheKey = self._getStructureCacheKey(x, y, direction, "")
            if cacheKey in self._structureCache:
                del self._structureCache[cacheKey]

        for direction, terrainType in self.lastPlacedCard.getTerrains().items(
        ):
            key = (x, y, direction)
            if not terrainType or key in self.structureMap:
                continue

            cacheKey = self._getStructureCacheKey(x, y, direction, terrainType)
            if cacheKey in self._structureCache:
                logger.debug(f"Using cached structure for {cacheKey}")
                cachedStructure = self._structureCache[cacheKey]
                if cachedStructure:
                    self.structureMap[key] = cachedStructure
                    cachedStructure.addCardSide(self.lastPlacedCard, direction)
                continue

            connectedSides = self.scanConnectedSides(x, y, direction,
                                                     terrainType)
            connectedStructures = {
                self.structureMap.get(side)
                for side in connectedSides if self.structureMap.get(side)
            }
            connectedStructures.discard(None)

            if connectedStructures:
                mainStructure = connectedStructures.pop()
                for s in connectedStructures:
                    mainStructure.merge(s)
                    self.structures.remove(s)
            else:
                mainStructure = Structure(terrainType.capitalize())
                self.structures.append(mainStructure)

            self._structureCache[cacheKey] = mainStructure

            for cx, cy, cdir in connectedSides:
                self.structureMap[(cx, cy, cdir)] = mainStructure
                mainStructure.addCardSide(self.gameBoard.getCard(cx, cy), cdir)

        self._structureCacheValid = True
        self._lastBoardHash = currentBoardHash

    def findConnectedStructures(self, x: int, y: int, direction: str,
                                terrainType: str, structureMap: dict) -> list:
        """Find existing structures connected to the given card side."""
        neighbors = {
            "N": (x, y - 1, "S"),
            "S": (x, y + 1, "N"),
            "E": (x + 1, y, "W"),
            "W": (x - 1, y, "E")
        }
        connected = []
        for dir, (nx, ny, ndir) in neighbors.items():
            if direction == dir:
                s = structureMap.get((nx, ny, ndir))
                if s and s.getStructureType().lower() == terrainType:
                    logger.debug(
                        f"Existing structure detected at ({nx}, {ny}) {ndir}")
                    connected.append(s)
        return list(set(connected))

    def scanConnectedSides(self, x: int, y: int, direction: str,
                           terrainType: str) -> set:
        """Collect all connected sides forming a continuous structure."""
        visited = set()
        stack = [(x, y, direction)]
        while stack:
            cx, cy, cdir = stack.pop()
            if (cx, cy, cdir) in visited:
                continue
            card = self.gameBoard.getCard(cx, cy)
            if not card:
                continue
            if card.getTerrains().get(cdir) != terrainType:
                continue
            visited.add((cx, cy, cdir))
            connectedDirs = card.getConnections().get(
                cdir, []) if card.getConnections() else []
            for dir2 in connectedDirs:
                if (cx, cy, dir2) not in visited:
                    stack.append((cx, cy, dir2))
            neighbors = {
                "N": (cx, cy - 1, "S"),
                "S": (cx, cy + 1, "N"),
                "E": (cx + 1, cy, "W"),
                "W": (cx - 1, cy, "E")
            }
            if terrainType == "field":
                edgeLineAdjacents = {
                    "N": [((cx - 1, cy), "N"), ((cx + 1, cy), "N")],
                    "S": [((cx - 1, cy), "S"), ((cx + 1, cy), "S")],
                    "E": [((cx, cy - 1), "E"), ((cx, cy + 1), "E")],
                    "W": [((cx, cy - 1), "W"), ((cx, cy + 1), "W")],
                }
                if cdir in edgeLineAdjacents:
                    for (nx, ny), ndir in edgeLineAdjacents[cdir]:
                        neighbor = self.gameBoard.getCard(nx, ny)
                        if neighbor and neighbor.getTerrains().get(
                                ndir) == terrainType:
                            if (nx, ny, ndir) not in visited:
                                stack.append((nx, ny, ndir))
            if cdir in neighbors:
                nx, ny, ndir = neighbors[cdir]
                neighbor = self.gameBoard.getCard(nx, ny)
                if neighbor and neighbor.getTerrains().get(
                        ndir) == terrainType:
                    stack.append((nx, ny, ndir))
        return visited

    def scoreStructure(self, structure: typing.Any) -> None:
        """Score a completed structure by awarding points to the majority owner(s)."""
        if not structure.getIsCompleted() and not self.gameOver:
            logger.debug("Structure is not completed, skipping scoring.")
            return
        score = structure.getScore(gameSession=self)
        owners = structure.getMajorityOwners()
        if not owners:
            logger.debug(
                f"{structure.structureType} was completed but there were no meeples to score"
            )
            return
        if not self.gameOver:
            logger.info(f"{structure.structureType} was completed")
        for owner in owners:
            logger.scoring(
                f"Player {owner.getName()} scored {score} points from the {structure.structureType}"
            )
            owner.addScore(score)

            if self.onShowNotification:
                message = f"Player {owner.getName()} scored {score} points from {structure.structureType}!"
                self.onShowNotification("success", message)

        structure.setColor(owners[0].getColorWithAlpha())
        for figure in structure.getFigures()[:]:
            structure.removeFigure(figure)
            figure.owner.addFigure(figure)
            logger.info(f"{figure.owner.getName()}'s figure was returned")

    def endGame(self) -> None:
        """End the game and score all incomplete structures."""
        logger.info("GAME OVER - No more cards in deck!")
        logger.scoring("Remaining incomplete structures will now be scored...")
        logger.debug("=== END OF GAME TRIGGERED ===")

        if self.onShowNotification:
            self.onShowNotification(
                "info", "Game Over! Scoring remaining structures...")

        self.gameOver = True
        for structure in self.structures:
            if not structure.getIsCompleted():
                logger.debug(
                    f"Scoring incomplete {structure.structureType}...")
                self.scoreStructure(structure)
        logger.debug("All meeples have been returned to players")
        self.placedFigures.clear()

        self._invalidateCandidateCache()
        self._invalidateStructureCache()
        self._invalidateValidationCache()
        self._invalidateNeighborCache()

        for player in self.players:
            if hasattr(player, 'invalidateEvaluationCache'):
                player.invalidateEvaluationCache()
            if hasattr(player, 'invalidateFigureCache'):
                player.invalidateFigureCache()

        if hasattr(self, 'onRenderCacheInvalidate'):
            self.onRenderCacheInvalidate()

        self.showFinalResults()
        if self.onTurnEnded:
            self.onTurnEnded()

    def showFinalResults(self) -> None:
        """Display the final scores."""
        logger.scoring("=== FINAL SCORES ===")
        sortedPlayers = sorted(self.players,
                               key=lambda p: p.getScore(),
                               reverse=True)

        if sortedPlayers and self.onShowNotification:
            winner = sortedPlayers[0]
            self.onShowNotification(
                "success",
                f"Player {winner.getName()} wins with {winner.getScore()} points!"
            )

        for i, player in enumerate(sortedPlayers):
            if i == 0:
                logger.scoring(
                    f"WINNER: {player.getName()}: {player.getScore()} points")
            else:
                logger.scoring(
                    f"{player.getName()}: {player.getScore()} points")

    def _getBoardStateHash(self) -> int:
        """Get a hash of the current board state for caching."""
        return len([(x, y) for y in range(self.gameBoard.getGridSize())
                    for x in range(self.gameBoard.getGridSize())
                    if self.gameBoard.getCard(x, y)])

    def _getStructureCacheKey(self, x: int, y: int, direction: str,
                              terrainType: str) -> tuple:
        """Get a cache key for structure detection."""
        return (x, y, direction, terrainType)

    def _getValidationCacheKey(self, card: typing.Any, x: int,
                               y: int) -> tuple:
        """Get a cache key for card validation."""
        return (id(card), x, y, card.rotation)

    def _updateCandidatePositions(self) -> None:
        """Update the cached candidate positions based on current board state."""
        currentState = self._getBoardStateHash()
        if self._lastBoardState == currentState:
            return

        self._lastBoardState = currentState
        self._candidatePositions.clear()

        occupiedPositions = set()
        for y in range(self.gameBoard.getGridSize()):
            for x in range(self.gameBoard.getGridSize()):
                if self.gameBoard.getCard(x, y):
                    occupiedPositions.add((x, y))

        for x, y in occupiedPositions:
            neighbors = self._getNeighborsCached(x, y)
            for nx, ny in neighbors:
                if not self.gameBoard.getCard(nx, ny):
                    self._candidatePositions.add((nx, ny))

    def getCandidatePositions(self) -> set:
        """Get all candidate positions where a card could potentially be placed."""
        self._updateCandidatePositions()
        return self._candidatePositions.copy()

    def _invalidateCandidateCache(self) -> None:
        """Invalidate the candidate positions cache."""
        self._lastBoardState = None
        self._candidatePositions.clear()

    def invalidateCandidateCache(self) -> None:
        """Public method to invalidate the candidate positions cache."""
        self._invalidateCandidateCache()

    def _invalidateStructureCache(self) -> None:
        """Invalidate the structure detection cache."""
        self._structureCache.clear()
        self._structureCacheValid = False
        self._lastBoardHash = None

    def invalidateStructureCache(self) -> None:
        """Public method to invalidate the structure detection cache."""
        self._invalidateStructureCache()

    def _invalidateValidationCache(self) -> None:
        """Invalidate the card validation cache."""
        self._validationCache.clear()
        self._validationCacheValid = False

    def invalidateValidationCache(self) -> None:
        """Public method to invalidate the card validation cache."""
        self._invalidateValidationCache()

    def _getNeighborsCached(self, x: int, y: int) -> set:
        """Get neighbor positions with caching."""
        if (x, y) in self._neighborCache:
            return self._neighborCache[(x, y)]

        neighbors = set()
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.gameBoard.getGridSize()
                    and 0 <= ny < self.gameBoard.getGridSize()):
                neighbors.add((nx, ny))

        self._neighborCache[(x, y)] = neighbors
        return neighbors

    def _invalidateNeighborCache(self) -> None:
        """Invalidate the neighbor lookup cache."""
        self._neighborCache.clear()
        self._neighborCacheValid = False

    def invalidateNeighborCache(self) -> None:
        """Public method to invalidate the neighbor lookup cache."""
        self._invalidateNeighborCache()

    def validateCardPlacementCached(self, card: typing.Any, x: int,
                                    y: int) -> bool:
        """Validate card placement with caching."""
        if not card:
            return False

        cacheKey = self._getValidationCacheKey(card, x, y)
        if cacheKey in self._validationCache:
            return self._validationCache[cacheKey]

        result = self.gameBoard.validateCardPlacement(card, x, y)

        self._validationCache[cacheKey] = result
        return result

    def getValidPlacements(self, card: typing.Any) -> set:
        """Get all valid placements for a specific card."""
        if not card:
            return set()

        candidates = self.getCandidatePositions()
        valid = set()

        originalRotation = card.rotation
        try:
            for x, y in candidates:
                for rotation in range(4):
                    if self.validateCardPlacementCached(card, x, y):
                        valid.add((x, y, card.rotation))
                    card.rotate()
        finally:
            while card.rotation != originalRotation:
                card.rotate()

        return valid

    def canPlaceCardAnywhere(self, card: typing.Any) -> bool:
        """Check if card can be placed anywhere on the board."""
        if not card:
            return False
        logger.debug("Checking if card can be placed anywhere on the board...")
        if self.isFirstRound:
            logger.debug("First round - card can always be placed")
            return True

        validPlacements = self.getValidPlacements(card)
        logger.debug(f"Found {len(validPlacements)} valid placements")

        return len(validPlacements) > 0

    def getRandomValidPlacement(self,
                                card: typing.Any) -> typing.Optional[tuple]:
        """Get a random valid placement for the given card."""
        if not card:
            return None

        validPlacements = list(self.getValidPlacements(card))
        if not validPlacements:
            return None

        x, y, rotation = random.choice(validPlacements)

        originalRotation = card.rotation
        while card.rotation != rotation:
            card.rotate()

        return (x, y, rotation)

    def serialize(self) -> dict:
        """Serialize the game session to a dictionary."""
        logger.debug("Serializing game state")
        return {
            "players": [player.serialize() for player in self.players],
            "deck": [card.serialize() for card in self.cardsDeck],
            "board":
            self.gameBoard.serialize(),
            "current_card":
            self.currentCard.serialize() if self.currentCard else None,
            "last_placed_card_position":
            self.gameBoard.getCardPosition(self.lastPlacedCard)
            if self.lastPlacedCard else None,
            "is_first_round":
            self.isFirstRound,
            "turn_phase":
            self.turnPhase,
            "game_over":
            self.gameOver,
            "current_player_index":
            self.currentPlayer.getIndex(),
            "placed_figures": [{
                **figure.serialize(), "card_position":
                self.gameBoard.getCardPosition(figure.card)
            } for figure in self.placedFigures if figure.card],
            "structure_map":
            list(self.structureMap.keys()),
            "structures": [
                s.serialize() for s in self.structures
                if hasattr(s, 'serialize')
            ],
            "game_mode":
            self.gameMode,
            "lobby_completed":
            self.lobbyCompleted,
            "network_mode":
            self.networkMode
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'GameSession':
        """Deserialize a game session from a dictionary."""
        players = []
        for p in data.get("players", []):
            try:
                if p["name"].startswith("AI_"):
                    players.append(AIPlayer.deserialize(p))
                else:
                    players.append(Player.deserialize(p))
            except Exception as e:
                logger.warning(f"Skipping malformed player entry: {p} - {e}")
        lobbyCompleted = data.get("lobby_completed", True)
        networkMode = data.get("network_mode", 'local')
        session = cls([p.getName() for p in players],
                      noInit=True,
                      lobbyCompleted=lobbyCompleted,
                      networkMode=networkMode)
        session.players = players
        try:
            session.currentPlayer = players[int(
                data.get("current_player_index", 0))]
        except (IndexError, ValueError, TypeError) as e:
            logger.warning(
                f"Invalid current_player_index, defaulting to first: {e}")
            session.currentPlayer = players[0] if players else None
        session.cardsDeck = []
        for c in data.get("deck", []):
            try:
                session.cardsDeck.append(Card.deserialize(c))
            except Exception as e:
                logger.warning(f"Skipping malformed card in deck: {c} - {e}")
        try:
            session.currentCard = Card.deserialize(
                data["current_card"]) if data.get("current_card") else None
        except Exception as e:
            logger.warning(f"Failed to deserialize currentCard - {e}")
            session.currentCard = None
        try:
            session.gameBoard = GameBoard.deserialize(data.get("board", {}))
        except Exception as e:
            logger.warning(f"Failed to deserialize gameBoard - {e}")
            session.gameBoard = GameBoard()
        try:
            lastPlacedCardPos = data.get("last_placed_card_position")
            if lastPlacedCardPos:
                x, y = lastPlacedCardPos
                session.lastPlacedCard = session.gameBoard.getCard(x, y)
            else:
                session.lastPlacedCard = None
        except Exception as e:
            logger.warning(
                f"Failed to deserialize lastPlacedCard position - {e}")
            session.lastPlacedCard = None
        try:
            session.isFirstRound = bool(data.get("is_first_round", True))
            session.turnPhase = int(data.get("turn_phase", 1))
            session.gameOver = bool(data.get("game_over", False))
        except Exception as e:
            logger.warning(f"Failed to parse basic session attributes - {e}")
        session.gameMode = data.get("game_mode", None)
        playerMap = {p.getIndex(): p for p in session.players}
        session.placedFigures = []
        for fdata in data.get("placed_figures", []):
            try:
                figure = Figure.deserialize(fdata, playerMap,
                                            session.gameBoard)
                if figure:
                    session.placedFigures.append(figure)
            except Exception as e:
                logger.warning(f"Skipping malformed figure: {fdata} - {e}")
        session.structures = []
        for s in data.get("structures", []):
            try:
                structure = Structure.deserialize(s, session.gameBoard,
                                                  playerMap,
                                                  session.placedFigures)
                if structure:
                    session.structures.append(structure)
            except Exception as e:
                logger.warning(f"Skipping malformed structure: {s} - {e}")
        session.structureMap = {}
        seenKeys = set()
        for structure in session.structures:
            for card, direction in structure.cardSides:
                pos = card.getPosition()
                if pos and pos["X"] is not None and pos["Y"] is not None:
                    key = (pos["X"], pos["Y"], direction)
                    if key in seenKeys:
                        logger.warning(
                            f"Duplicate structure mapping detected during rebuild: {key}"
                        )
                    session.structureMap[key] = structure
                    seenKeys.add(key)
        figLookup = {
            (f.card, f.positionOnCard): f
            for f in session.placedFigures
        }
        for structure in session.structures:
            updatedFigures = []
            for fig in structure.getFigures():
                key = (fig.card, fig.positionOnCard)
                updatedFigures.append(figLookup.get(key, fig))
            structure.setFigures(updatedFigures)
        return session
