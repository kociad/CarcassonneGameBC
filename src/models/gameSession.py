import random
import logging
import typing

from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from models.structure import Structure
from models.aiPlayer import AIPlayer
from models.figure import Figure
import settings

logger = logging.getLogger(__name__)

class GameSession:
    """Manages the overall game state, including players, board, and card placement."""
    def __init__(self, playerNames: list[str], noInit: bool = False, lobbyCompleted: bool = True, networkMode: str = 'local') -> None:
        """
        Initialize the game session with players, board, and card deck.
        :param playerNames: List of player names to create Player instances.
        :param noInit: If True, skip player and deck initialization.
        """
        self.gameBoard = GameBoard()
        self.cardsDeck = None
        self.players = []
        self.currentPlayer = None
        self.structures = []
        self.gameMode = None
        self.currentCard = None
        self.lastPlacedCard = None
        self.isFirstRound = True
        self.placedFigures = []
        self.turnPhase = 1
        self.structureMap = {}
        self.gameOver = False
        self.onTurnEnded = None
        self.onShowNotification = None
        self.lobbyCompleted = lobbyCompleted
        self.networkMode = networkMode
        
        self.gameHistory = []
        self.maxHistorySize = 50  # Limit history to prevent memory issues
        
        if not noInit:
            self.generatePlayerList(playerNames)
            self.cardsDeck = self.generateCardsDeck()
            self.shuffleCardsDeck(self.cardsDeck)
            self.placeStartingCard()

    def saveGameState(self) -> None:
        """Save the current game state to history for undo functionality."""
        try:
            gameState = self.serialize()
            self.gameHistory.append(gameState)
            
            if len(self.gameHistory) > self.maxHistorySize:
                self.gameHistory.pop(0)
                
            logger.debug(f"Game state saved. History size: {len(self.gameHistory)}")
        except Exception as e:
            logger.error(f"Failed to save game state: {e}")

    def canUndo(self) -> bool:
        """Check if undo is available."""
        return len(self.gameHistory) > 0

    def undo(self) -> bool:
        """Restore the previous game state."""
        if not self.canUndo():
            logger.warning("No game states available for undo")
            return False
            
        try:
            previousState = self.gameHistory.pop()
            restoredSession = GameSession.deserialize(previousState)
            
            self.gameBoard = restoredSession.gameBoard
            self.cardsDeck = restoredSession.cardsDeck
            self.players = restoredSession.players
            self.currentPlayer = restoredSession.currentPlayer
            self.structures = restoredSession.structures
            self.gameMode = restoredSession.gameMode
            self.currentCard = restoredSession.currentCard
            self.isFirstRound = restoredSession.isFirstRound
            self.placedFigures = restoredSession.placedFigures
            self.turnPhase = restoredSession.turnPhase
            self.structureMap = restoredSession.structureMap
            self.gameOver = restoredSession.gameOver
            self.lobbyCompleted = restoredSession.lobbyCompleted
            self.networkMode = restoredSession.networkMode
            
            self.lastPlacedCard = restoredSession.lastPlacedCard
            
            if hasattr(restoredSession, 'onTurnEnded'):
                self.onTurnEnded = restoredSession.onTurnEnded
            if hasattr(restoredSession, 'onShowNotification'):
                self.onShowNotification = restoredSession.onShowNotification
                
            logger.debug("Game state restored from history")
            return True
        except Exception as e:
            logger.error(f"Failed to restore game state: {e}")
            return False

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

    def generatePlayerList(self, playerNames: list[str]) -> None:
        """Generate a list of indexed players for the game."""
        logger.debug("Generating a list of players...")
        colors = ["blue", "red", "green", "pink", "yellow", "black"]
        random.shuffle(colors)
        if playerNames:
            index = 0
            for player in playerNames:
                if player.startswith("AI_"):
                    self.players.append(AIPlayer(player, index, colors.pop()))
                else:
                    self.players.append(Player(player, index, colors.pop()))
                index += 1
            self.currentPlayer = self.players[len(self.players) - 1]
        logger.debug("Player list generated")

    def generateCardsDeck(self) -> list:
        """Generate a deck of cards for the game."""
        logger.debug("Generating deck...")
        card_definitions = [
            {"image": "Base_Game_C3_Tile_A.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "field", "C": "monastery"}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_B.png", "terrains": {"N": "field", "E": "field", "S": "field", "W": "field", "C": "monastery"}, "connections": {"N": ["E", "S", "W"], "E": ["S", "W", "N"], "S": ["W", "N", "E"], "W": ["N", "E", "S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_C.png", "terrains": {"N": "city", "E": "city", "S": "city", "W": "city", "C": None}, "connections": {"N": ["E", "S", "W"], "E": ["S", "W", "N"], "S": ["W", "N", "E"], "W": ["N", "E", "S"]}, "features": ["coat"]},
            {"image": "Base_Game_C3_Tile_D.png", "terrains": {"N": "city", "E": "road", "S": "field", "W": "road", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_E.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "field", "C": None}, "connections": {"E": ["S", "W"], "S": ["W", "E"], "W": ["E", "S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_F.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": ["coat"]},
            {"image": "Base_Game_C3_Tile_G.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_H.png", "terrains": {"N": "city", "E": "field", "S": "city", "W": "field", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_I.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "city", "C": None}, "connections": {"E": ["S"], "S": ["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_J.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "field", "C": None}, "connections": {"E": ["S"], "S": ["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_K.png", "terrains": {"N": "city", "E": "field", "S": "road", "W": "road", "C": None}, "connections": {"S": ["W"], "W": ["S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_L.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None},
            {"image": "Base_Game_C3_Tile_M.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections": {"N": ["E"], "E": ["N"], "S": ["W"], "W": ["S"]}, "features": ["coat"]},
            {"image": "Base_Game_C3_Tile_N.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections": {"N": ["E"], "E": ["N"], "S": ["W"], "W": ["S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_O.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections": {"N": ["W"], "E": ["S"], "S": ["E"], "W": ["N"]}, "features": ["coat"]},
            {"image": "Base_Game_C3_Tile_P.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections": {"N": ["W"], "E": ["S"], "S": ["E"], "W": ["N"]}, "features": None},
            {"image": "Base_Game_C3_Tile_Q.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": ["coat"]},
            {"image": "Base_Game_C3_Tile_R.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_S.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": ["coat"]},
            {"image": "Base_Game_C3_Tile_T.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_U.png", "terrains": {"N": "road", "E": "field", "S": "road", "W": "field", "C": None}, "connections": {"N": ["S"], "S": ["N"]}, "features": None},
            {"image": "Base_Game_C3_Tile_V.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "road", "C": None}, "connections": {"N": ["E"], "E": ["N"], "S": ["W"], "W": ["S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_W.png", "terrains": {"N": "field", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None},
            {"image": "Base_Game_C3_Tile_X.png", "terrains": {"N": "road", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None}
        ]
        card_distributions = {
            "Base_Game_C3_Tile_A.png": 2,
            "Base_Game_C3_Tile_B.png": 4,
            "Base_Game_C3_Tile_C.png": 1,
            "Base_Game_C3_Tile_D.png": 4,
            "Base_Game_C3_Tile_E.png": 5,
            "Base_Game_C3_Tile_F.png": 2,
            "Base_Game_C3_Tile_G.png": 1,
            "Base_Game_C3_Tile_H.png": 3,
            "Base_Game_C3_Tile_I.png": 2,
            "Base_Game_C3_Tile_J.png": 3,
            "Base_Game_C3_Tile_K.png": 3,
            "Base_Game_C3_Tile_L.png": 3,
            "Base_Game_C3_Tile_M.png": 2,
            "Base_Game_C3_Tile_N.png": 3,
            "Base_Game_C3_Tile_O.png": 2,
            "Base_Game_C3_Tile_P.png": 3,
            "Base_Game_C3_Tile_Q.png": 1,
            "Base_Game_C3_Tile_R.png": 3,
            "Base_Game_C3_Tile_S.png": 2,
            "Base_Game_C3_Tile_T.png": 1,
            "Base_Game_C3_Tile_U.png": 8,
            "Base_Game_C3_Tile_V.png": 9,
            "Base_Game_C3_Tile_W.png": 4,
            "Base_Game_C3_Tile_X.png": 1
        }
        cards = []
        for card in card_definitions:
            image = card["image"]
            terrains = card["terrains"]
            connections = card["connections"]
            features = card["features"]
            count = card_distributions.get(image, 1)
            cards.extend([Card(settings.TILE_IMAGES_PATH + image, terrains, connections, features) for _ in range(count)])
        logger.debug("Deck generated")
        return cards

    def shuffleCardsDeck(self, deck: list) -> None:
        """Shuffle an existing deck of cards."""
        logger.debug("Shuffling deck...")
        random.shuffle(deck)
        logger.debug("Deck shuffled")

    def placeStartingCard(self) -> None:
        """Place the first card automatically at the center of the board."""
        logger.debug("Playing first turn...")
        center_x, center_y = self.gameBoard.getCenterPosition()
        if self.cardsDeck:
            if self.playCard(center_x, center_y):
                self.isFirstRound = False
                logger.debug("First turn played")
                self.nextTurn()
        else:
            logger.debug("Unable to play first round, no cardsDeck available")

    def drawCard(self) -> typing.Any:
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
            logger.info(f"{self.currentPlayer.getName()}'s turn (Player {self.currentPlayer.getIndex() + 1})")
            self.currentCard = self.drawCard()
            if self.currentCard:
                logger.info(f"New card drawn - {len(self.cardsDeck)} cards remaining")
            self.turnPhase = 1
            if self.onTurnEnded:
                self.onTurnEnded()
        else:
            self.endGame()

    def playCard(self, x: int, y: int) -> bool:
        """Play the card placing part of the turn."""
        logger.debug("Playing card...")
        card = self.currentCard
        if not card:
            if not self.cardsDeck:
                logger.debug("Unable to play turn, no card is selected and no cardsDeck is available")
                return False
            card = self.drawCard()
        if not self.gameBoard.validateCardPlacement(card, x, y) and not self.isFirstRound:
            logger.debug(f"Player {self.currentPlayer.getName()} was unable to place card, placement is invalid")
            if self.onShowNotification and not self.currentPlayer.getIsAI():
                self.onShowNotification("error", "Cannot place card here - terrain doesn't match adjacent cards!")
            return False
        self.gameBoard.placeCard(card, x, y)
        self.lastPlacedCard = card
        self.currentCard = None
        if not self.isFirstRound:
            logger.info(f"Player {self.currentPlayer.getName()} placed a card at [{x - self.gameBoard.getCenter()},{self.gameBoard.getCenter() - y}]")
        logger.debug(f"Last played card set to card {card} at {x};{y}")
        self.detectStructures()
        return True

    def discardCurrentCard(self) -> None:
        """Discard the currently selected card and select a new one."""
        if self.currentCard:
            self.currentCard = self.drawCard()

    def playAITurn(self, player: typing.Any = None) -> None:
        """If the current player is AI, trigger their turn."""
        if player is None:
            player = self.currentPlayer
        if isinstance(player, AIPlayer):
            player.playTurn(self)
            return

    def playTurn(self, x: int, y: int, position: str = "C", player: typing.Any = None) -> None:
        """Play a single complete game turn in two phases."""
        if player is None:
            player = self.currentPlayer
        
        if self.turnPhase == 1:
            logger.debug("Turn Phase 1: Attempting to place card...")
            self.saveGameState()
            if self.playCard(x, y):
                self.turnPhase = 2
            else:
                logger.debug("Card placement failed.")
            return
        elif self.turnPhase == 2:
            logger.debug("Turn Phase 2: Attempting to place figure...")
            self.saveGameState()
            if self.playFigure(player, x, y, position):
                logger.debug("Figure placed.")
            else:
                logger.debug("Figure not placed or skipped.")
                if self.gameHistory:
                    self.gameHistory.pop()
                return
            logger.debug("Checking completed structures...")
            for structure in self.structures:
                structure.checkCompletion()
                if structure.getIsCompleted():
                    logger.debug(f"Structure {structure.structureType} is completed!")
                    self.scoreStructure(structure)
            self.nextTurn()

    def skipCurrentAction(self) -> None:
        """Skip the current phase action with official rules validation."""
        if self.turnPhase == 1:
            logger.debug("Attempting to skip card placement...")
            self.saveGameState()
            if self.canPlaceCardAnywhere(self.currentCard):
                logger.debug(f"Player {self.currentPlayer.getName()} was unable to skip card placement - card can be placed somewhere on the board")
                if self.onShowNotification and not self.currentPlayer.getIsAI():
                    self.onShowNotification("warning", "Cannot discard card - it can be placed on the board!")
            else:
                logger.info(f"Player {self.currentPlayer.getName()} discarded card - no valid placement was found")
                self.discardCurrentCard()
                if not self.cardsDeck:
                    self.endGame()
        elif self.turnPhase == 2:
            logger.info(f"Player {self.currentPlayer.getName()} skipped meeple placement")
            self.saveGameState()
            logger.debug("Finalizing turn...")
            for structure in self.structures:
                structure.checkCompletion()
                if structure.getIsCompleted():
                    self.scoreStructure(structure)
            self.nextTurn()
            self.turnPhase = 1

    def playFigure(self, player: typing.Any, x: int, y: int, position: str) -> bool:
        """Place a figure on a valid card position."""
        logger.debug("Playing figure...")
        card = self.gameBoard.getCard(x, y)
        if card != self.lastPlacedCard:
            logger.debug(f"Player {player.getName()} was unable to play figure on card {self.gameBoard.getCard(x,y)} at [{x},{y}], can only place figures on last played card")
            if self.onShowNotification and not player.getIsAI():
                self.onShowNotification("error", "Cannot place meeple here - only on the card you just placed!")
            return False
        if not card:
            logger.debug(f"Player {player.getName()} was unable to place their meeple at [{x},{y}], no card was found.")
            if self.onShowNotification and not player.getIsAI():
                self.onShowNotification("error", "No card found at this position!")
            return False
        structure = self.structureMap.get((x, y, position))
        if structure:
            if structure.figures:
                logger.debug(f"Player {player.getName()} was unable to place their meeple at [{x},{y}], position {position}, the structure is already occupied")
                if self.onShowNotification and not player.getIsAI():
                    self.onShowNotification("error", "Cannot place meeple - this structure is already occupied!")
                return False
        if player.figures:
            figure = player.getFigure()
            if figure.place(card, position):
                self.placedFigures.append(figure)
                logger.info(f"Player {player.getName()} placed a meeple on {position} position at [{x - self.gameBoard.getCenter()},{self.gameBoard.getCenter() - y}]")
                if structure:
                    structure.addFigure(figure)
                logger.debug("Figure played")
                return True
            else:
                player.addFigure(figure)
        logger.debug(f"Player {player.getName()} was unable to place their meeple, player has no meeples left")
        if self.onShowNotification and not player.getIsAI():
            self.onShowNotification("error", "No meeples left to place!")
        return False

    def detectStructures(self) -> None:
        """Update structures based only on the last placed card."""
        logger.debug("Updating structures based on the last placed card...")
        if not self.lastPlacedCard:
            logger.debug("No card was placed. Skipping structure detection.")
            return
        position = self.gameBoard.getCardPosition(self.lastPlacedCard)
        if not position:
            logger.debug("Last placed card position not found.")
            return
        x, y = position
        self.visited = set()
        for direction, terrainType in self.lastPlacedCard.getTerrains().items():
            key = (x, y, direction)
            if not terrainType or key in self.structureMap:
                continue
            connected_sides = self.scanConnectedSides(x, y, direction, terrainType)
            connected_structures = {self.structureMap.get(side) for side in connected_sides if self.structureMap.get(side)}
            connected_structures.discard(None)
            if connected_structures:
                mainStructure = connected_structures.pop()
                for s in connected_structures:
                    mainStructure.merge(s)
                    self.structures.remove(s)
            else:
                mainStructure = Structure(terrainType.capitalize())
                self.structures.append(mainStructure)
            for cx, cy, cdir in connected_sides:
                self.structureMap[(cx, cy, cdir)] = mainStructure
                mainStructure.addCardSide(self.gameBoard.getCard(cx, cy), cdir)

    def findConnectedStructures(self, x: int, y: int, direction: str, terrainType: str, structureMap: dict) -> list:
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
                    logger.debug(f"Existing structure detected at ({nx}, {ny}) {ndir}")
                    connected.append(s)
        return list(set(connected))

    def scanConnectedSides(self, x: int, y: int, direction: str, terrainType: str) -> set:
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
            connectedDirs = card.getConnections().get(cdir, []) if card.getConnections() else []
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
                        if neighbor and neighbor.getTerrains().get(ndir) == terrainType:
                            if (nx, ny, ndir) not in visited:
                                stack.append((nx, ny, ndir))
            if cdir in neighbors:
                nx, ny, ndir = neighbors[cdir]
                neighbor = self.gameBoard.getCard(nx, ny)
                if neighbor and neighbor.getTerrains().get(ndir) == terrainType:
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
            logger.debug(f"{structure.structureType} was completed but there were no meeples to score")
            return
        if not self.gameOver:
            logger.info(f"{structure.structureType} was completed")
        for owner in owners:
            logger.scoring(f"Player {owner.getName()} scored {score} points from the {structure.structureType}")
            owner.addScore(score)
        structure.setColor(owners[0].getColorWithAlpha())
        for figure in structure.getFigures()[:]:
            structure.removeFigure(figure)
            figure.owner.addFigure(figure)
            logger.info(f"{figure.owner.getName()}'s meeple was returned")

    def endGame(self) -> None:
        """End the game and score all incomplete structures."""
        logger.info("GAME OVER - No more cards in deck!")
        logger.scoring("Remaining incomplete structures will now be scored...")
        logger.debug("=== END OF GAME TRIGGERED ===")
        self.gameOver = True
        for structure in self.structures:
            if not structure.getIsCompleted():
                logger.debug(f"Scoring incomplete {structure.structureType}...")
                self.scoreStructure(structure)
        logger.debug("All meeples have been returned to players")
        self.placedFigures.clear()
        self.showFinalResults()
        if self.onTurnEnded:
            self.onTurnEnded()

    def showFinalResults(self) -> None:
        """Display the final scores."""
        logger.scoring("=== FINAL SCORES ===")
        sortedPlayers = sorted(self.players, key=lambda p: p.getScore(), reverse=True)
        for i, player in enumerate(sortedPlayers):
            if i == 0:
                logger.scoring(f"WINNER: {player.getName()}: {player.getScore()} points")
            else:
                logger.scoring(f"{player.getName()}: {player.getScore()} points")

    def getCandidatePositions(self) -> set:
        """Get all candidate positions where a card could potentially be placed."""
        candidatePositions = set()
        gridSize = self.gameBoard.getGridSize()
        for y in range(gridSize):
            for x in range(gridSize):
                if self.gameBoard.getCard(x, y):
                    neighbors = [
                        (x + 1, y),
                        (x - 1, y),
                        (x, y + 1),
                        (x, y - 1)
                    ]
                    for nx, ny in neighbors:
                        if 0 <= nx < gridSize and 0 <= ny < gridSize:
                            if not self.gameBoard.getCard(nx, ny):
                                candidatePositions.add((nx, ny))
        return candidatePositions

    def canPlaceCardAnywhere(self, card: typing.Any) -> bool:
        """Check if card can be placed anywhere on the board."""
        if not card:
            return False
        logger.debug("Checking if card can be placed anywhere on the board...")
        if self.isFirstRound:
            logger.debug("First round - card can always be placed")
            return True
        candidatePositions = self.getCandidatePositions()
        logger.debug(f"Found {len(candidatePositions)} candidate positions to check")
        if not candidatePositions:
            logger.debug("No candidate positions found")
            return False
        originalRotation = card.rotation
        try:
            for x, y in candidatePositions:
                while card.rotation != originalRotation:
                    card.rotate()
                for rotation in range(4):
                    if self.gameBoard.validateCardPlacement(card, x, y):
                        logger.debug(f"Card can be placed at ({x}, {y}) with rotation {card.rotation} 6")
                        return True
                    card.rotate()
            logger.debug("Card cannot be placed at any candidate position")
            return False
        finally:
            while card.rotation != originalRotation:
                card.rotate()

    def getRandomValidPlacement(self, card: typing.Any) -> typing.Optional[tuple]:
        """Get a random valid placement for the given card."""
        if not card:
            return None
        candidatePositions = list(self.getCandidatePositions())
        random.shuffle(candidatePositions)
        originalRotation = card.rotation
        try:
            for x, y in candidatePositions:
                while card.rotation != originalRotation:
                    card.rotate()
                for rotations in range(4):
                    if self.gameBoard.validateCardPlacement(card, x, y):
                        return (x, y, rotations)
                    card.rotate()
            return None
        finally:
            while card.rotation != originalRotation:
                card.rotate()

    def serialize(self) -> dict:
        """Serialize the game session to a dictionary."""
        logger.debug("Serializing game state")
        return {
            "players": [player.serialize() for player in self.players],
            "deck": [card.serialize() for card in self.cardsDeck],
            "board": self.gameBoard.serialize(),
            "current_card": self.currentCard.serialize() if self.currentCard else None,
            "last_placed_card_position": self.gameBoard.getCardPosition(self.lastPlacedCard) if self.lastPlacedCard else None,
            "is_first_round": self.isFirstRound,
            "turn_phase": self.turnPhase,
            "game_over": self.gameOver,
            "current_player_index": self.currentPlayer.getIndex(),
            "placed_figures": [
                {
                    **figure.serialize(),
                    "card_position": self.gameBoard.getCardPosition(figure.card)
                }
                for figure in self.placedFigures if figure.card
            ],
            "structure_map": list(self.structureMap.keys()),
            "structures": [s.serialize() for s in self.structures if hasattr(s, 'serialize')],
            "game_mode": self.gameMode,
            "lobby_completed": self.lobbyCompleted,
            "network_mode": self.networkMode
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
        session = cls([p.getName() for p in players], noInit=True, lobbyCompleted=lobbyCompleted, networkMode=networkMode)
        session.players = players
        try:
            session.currentPlayer = players[int(data.get("current_player_index", 0))]
        except (IndexError, ValueError, TypeError) as e:
            logger.warning(f"Invalid current_player_index, defaulting to first: {e}")
            session.currentPlayer = players[0] if players else None
        session.cardsDeck = []
        for c in data.get("deck", []):
            try:
                session.cardsDeck.append(Card.deserialize(c))
            except Exception as e:
                logger.warning(f"Skipping malformed card in deck: {c} - {e}")
        try:
            session.currentCard = Card.deserialize(data["current_card"]) if data.get("current_card") else None
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
            logger.warning(f"Failed to deserialize lastPlacedCard position - {e}")
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
                figure = Figure.deserialize(fdata, playerMap, session.gameBoard)
                if figure:
                    session.placedFigures.append(figure)
            except Exception as e:
                logger.warning(f"Skipping malformed figure: {fdata} - {e}")
        session.structures = []
        for s in data.get("structures", []):
            try:
                structure = Structure.deserialize(s, session.gameBoard, playerMap, session.placedFigures)
                if structure:
                    session.structures.append(structure)
            except Exception as e:
                logger.warning(f"Skipping malformed structure: {s} - {e}")
        session.structureMap = {}
        seen_keys = set()
        for structure in session.structures:
            for card, direction in structure.cardSides:
                pos = card.getPosition()
                if pos and pos["X"] is not None and pos["Y"] is not None:
                    key = (pos["X"], pos["Y"], direction)
                    if key in seen_keys:
                        logger.warning(f"Duplicate structure mapping detected during rebuild: {key}")
                    session.structureMap[key] = structure
                    seen_keys.add(key)
        fig_lookup = {
            (f.card, f.positionOnCard): f
            for f in session.placedFigures
        }
        for structure in session.structures:
            updated_figures = []
            for fig in structure.getFigures():
                key = (fig.card, fig.positionOnCard)
                updated_figures.append(fig_lookup.get(key, fig))
            structure.setFigures(updated_figures)
        return session
