import random
import logging

from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from models.structure import Structure
from models.aiPlayer import AIPlayer
from models.figure import Figure

import settings

logger = logging.getLogger(__name__)

class GameSession:
    """
    Manages the overall game state, including players, board, and card placement.
    """
    
    def __init__(self, playerNames, noInit=False):
        """
        Initializes the game session with players, board, and card deck.
        :param player_names: List of player names to create Player instances.
        """
        self.gameBoard = GameBoard()
        self.cardsDeck = None
        self.players = [] # List of players in the game
        self.currentPlayer = None # Currently playing player
        self.structures = []
        self.gameMode = None # Currently unused
        self.currentCard = None # Currently selected card
        self.lastPlacedCard = None # Last placed card
        self.isFirstRound = True # Is this the first (automatic) round?
        self.placedFigures = [] # List of figures currently placed
        self.turnPhase = 1 # Tracking current turn phase
        self.structureMap = {}
        self.gameOver = False # Tracking game status
        
        self.onTurnEnded = None  # External callback for sync
        self.onShowNotification = None  # Callback for UI notifications
        
        if not noInit:
            # Create a list of players
            self.generatePlayerList(playerNames)
            
            # Generate new card deck based on specified definitions and distributions
            self.cardsDeck = self.generateCardsDeck()
            
            # Shuffle the new deck
            self.shuffleCardsDeck(self.cardsDeck)
                    
            # Automatically place the starting card
            self.placeStartingCard()
            
    def getPlayers(self):
        """
        Player list getter method
        :return: List of player objects
        """
        return self.players
        
    def getGameOver(self):
        """
        Game session game over getter method
        :return: True if game is over, False otherwise
        """
        return self.gameOver
        
    def getCurrentCard(self):
        """
        Current card getter method
        :return: Currently drawn card for current game session
        """
        return self.currentCard
        
    def getGameBoard(self):
        """
        Game board getter method
        :return: Game board used by the curent game session
        """
        return self.gameBoard
        
    def getCardsDeck(self):
        """
        Cards deck getter method
        :return: Cards deck assigned to current game session
        """
        return self.cardsDeck
        
    def getCurrentPlayer(self):
        """
        Current player getter method
        :return: Player currently having their turn
        """
        return self.currentPlayer
        
    def getPlacedFigures(self):
        """
        Placed figures getter method
        :return: List of figures placed on the board
        """
        return self.placedFigures
        
    def getStructures(self):
        """
        Structures getter method
        :return: List of detected structures
        """
        return self.structures
        
    def setTurnPhase(self, phase):
        """
        Turn phase setter method
        :param phase: Integer for the number of the phase to be set (1-2)
        """
        self.turnPhase=phase
        
    def getIsFirstRound(self):
        """
        First round status getter method
        :return: True if is first round False otherwise
        """
        #logger.debug("This is the first round")
        return self.isFirstRound
        
    def generatePlayerList(self, playerNames):
        """
        Generates a list of indexed players for the game
        :param playerNames: A list of player names
        """
        logger.debug("Generating a list of players...")
        
        colors = [
            "blue",
            "red",
            "green",
            "pink",
            "yellow",
            "black"
        ]
        
        random.shuffle(colors)
        
        if playerNames:
            index = 0
            
            for player in playerNames:
                if player.startswith("AI_"):
                    self.players.append(AIPlayer(player, index, colors.pop()))
                else:
                    self.players.append(Player(player, index, colors.pop()))
                index += 1
            
            self.currentPlayer=self.players[len(self.players)-1] # Last player is selected so that after playing the first turn, the turn is automatically advanced to the first player
            
        logger.debug("Player list generated")
        
    def generateCardsDeck(self):
        """
        Generates a deck of cards for the game.
        :return: A list of Card objects representing the card deck.
        """
        logger.debug("Generating deck...")
        
        card_definitions = [
            {"image": "Base_Game_C3_Tile_A.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "field", "C": "monastery"}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_B.png", "terrains": {"N": "field", "E": "field", "S": "field", "W": "field", "C": "monastery"}, "connections":{"N":["E","S","W"],"E":["S","W","N"],"S":["W","N","E"],"W":["N","E","S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_C.png", "terrains": {"N": "city", "E": "city", "S": "city", "W": "city", "C": None}, "connections":{"N":["E","S","W"],"E":["S","W","N"],"S":["W","N","E"],"W":["N","E","S"]}, "features":["coat"]},
            {"image": "Base_Game_C3_Tile_D.png", "terrains": {"N": "city", "E": "road", "S": "field", "W": "road", "C": None}, "connections":{"E":["W"], "W":["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_E.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "field", "C": None}, "connections":{"E":["S","W"],"S":["W","E"],"W":["E","S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_F.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"E":["W"],"W":["E"]}, "features":["coat"]},
            {"image": "Base_Game_C3_Tile_G.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"E":["W"],"W":["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_H.png", "terrains": {"N": "city", "E": "field", "S": "city", "W": "field", "C": None}, "connections":{"E":["W"],"W":["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_I.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "city", "C": None}, "connections":{"E":["S"],"S":["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_J.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "field", "C": None}, "connections":{"E":["S"],"S":["E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_K.png", "terrains": {"N": "city", "E": "field", "S": "road", "W": "road", "C": None}, "connections":{"S":["W"],"W":["S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_L.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None},
            {"image": "Base_Game_C3_Tile_M.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections":{"N":["E"],"E":["N"],"S":["W"],"W":["S"]}, "features":["coat"]},
            {"image": "Base_Game_C3_Tile_N.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections":{"N":["E"],"E":["N"],"S":["W"],"W":["S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_O.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections":{"N":["W"],"E":["S"],"S":["E"],"W":["N"]}, "features":["coat"]},
            {"image": "Base_Game_C3_Tile_P.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections":{"N":["W"],"E":["S"],"S":["E"],"W":["N"]}, "features": None},
            {"image": "Base_Game_C3_Tile_Q.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}, "features":["coat"]},
            {"image": "Base_Game_C3_Tile_R.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_S.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}, "features":["coat"]},
            {"image": "Base_Game_C3_Tile_T.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}, "features": None},
            {"image": "Base_Game_C3_Tile_U.png", "terrains": {"N": "road", "E": "field", "S": "road", "W": "field", "C": None}, "connections":{"N":["S"],"S":["N"]}, "features": None},
            {"image": "Base_Game_C3_Tile_V.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "road", "C": None}, "connections":{"N":["E"],"E":["N"],"S":["W"],"W":["S"]}, "features": None},
            {"image": "Base_Game_C3_Tile_W.png", "terrains": {"N": "field", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None},
            {"image": "Base_Game_C3_Tile_X.png", "terrains": {"N": "road", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None}
            # Add more card definitions as needed...
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
            count = card_distributions.get(image, 1)  # Default to 1 if not listed in distributions
            cards.extend([Card(settings.TILE_IMAGES_PATH + image, terrains, connections, features) for card in range(count)])
            
        logger.debug("Deck generated")
        return cards
        
    def shuffleCardsDeck(self, deck):
        """
        Shuffles an existing deck of cards
        :param deck: Existing card deck
        :return: Shuffled deck
        """
        logger.debug("Shuffling deck...")
        
        random.shuffle(deck)
        
        logger.debug("Deck shuffled")
    
    def placeStartingCard(self):
        """
        Plays the first turn automatically (places first card)
        """
        logger.debug("Playing first turn...")
        center_x, center_y = self.gameBoard.getCenterPosition()
        if self.cardsDeck:
            if self.playCard(center_x,center_y):
                self.isFirstRound = False
                logger.debug("First turn played")
                self.nextTurn()
        else:
            logger.debug("Unable to play first round, no cardsDeck available")
    
    def drawCard(self):
        """
        Draws a card from the deck for the current player.
        :return: The drawn card if available, otherwise None.
        """
        logger.debug("Drawing card...")
        if self.cardsDeck:
            logger.debug("Card drawn")
            return self.cardsDeck.pop(0)
            
        return None
    
    def nextTurn(self):
        """
        Moves to the next player's turn.
        """
        if self.cardsDeck:
            logger.debug("Advancing player turn...")
            
            currentIndex = self.currentPlayer.getIndex()
            nextIndex = (currentIndex + 1) % len(self.players)
            
            for player in self.players:
                if player.getIndex() == nextIndex:
                    self.currentPlayer = player
                    break
                    
            logger.info(f"{self.currentPlayer.getName()}'s turn (Player {self.currentPlayer.getIndex() + 1})")
            #logger.debug(f"New player {self.currentPlayer.getName()} index - {self.currentPlayer.getIndex()}")
            
            self.currentCard = self.drawCard()
            if self.currentCard:
                logger.info(f"New card drawn - {len(self.cardsDeck)} cards remaining")
            
            self.turnPhase = 1
            if self.onTurnEnded:
                self.onTurnEnded()
        else:
            self.endGame()
        
    def playCard(self, x, y):
        """
        Plays the card placing part of the turn
        """
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
            logger.info(f"{self.currentPlayer.getName()} placed a card at ({x}, {y})")
            
        logger.debug(f"Last played card set to card {card} at {x};{y}")
        
        self.detectStructures()
        return True
        
    def discardCurrentCard (self):
        """
        Discards current selected card and selects a new one
        """
        if self.currentCard:
            self.currentCard = self.drawCard()
            
    def playAITurn(self, player=None):
        """
        Checks if current player is AI and if so, triggers their turn
        """
        if player is None:
            player = self.currentPlayer
            
        if isinstance(player, AIPlayer):
            player.playTurn(self)
            return
        
    def playTurn(self, x, y, position="C", player=None):
        """
        Plays a single complete game turn in two phases:
        Phase 1 (turnPhase == 1): Attempts to place the current card at (x, y)
        Phase 2 (turnPhase == 2): Attempts to place a figure on (x, y), then finishes turn
        """
        if player is None:
            player = self.currentPlayer

        # Phase 1: Place Card
        if self.turnPhase == 1:
            logger.debug("Turn Phase 1: Attempting to place card...")
            if self.playCard(x, y):
                self.turnPhase = 2  # Move to figure placement phase
            else:
                logger.debug("Card placement failed.")
                
            #self.detectStructures() # Structure detection needs to be performed after each action
            
            return  # Wait for next player click (figure phase or retry)

        # Phase 2: Place Figure
        elif self.turnPhase == 2:
            logger.debug("Turn Phase 2: Attempting to place figure...")

            if self.playFigure(player, x, y, position):  # Defaulting to center — position must be set properly by event handler
                logger.debug("Figure placed.")
            else:
                logger.debug("Figure not placed or skipped.")
                return # Wait for next player action (retry figure placement or skip)

            #self.detectStructures() # Structure detection needs to be performed after each action

            logger.debug("Checking completed structures...")
            for structure in self.structures:
                structure.checkCompletion()
                if structure.getIsCompleted():
                    logger.debug(f"Structure {structure.structureType} is completed!")
                    self.scoreStructure(structure)

            self.nextTurn()
            
    def skipCurrentAction(self):
        """
        Skips the current phase action with official rules validation
        """
        if self.turnPhase == 1:
            logger.debug("Attempting to skip card placement...")
            
            if self.canPlaceCardAnywhere(self.currentCard):
                #logger.info("Cannot discard card - it can be placed somewhere on the board")
                logger.debug(f"Player {self.currentPlayer.getName()} was unable to skip card placement - card can be placed somewhere on the board")
                
                if self.onShowNotification and not self.currentPlayer.getIsAI():
                    self.onShowNotification("warning", "Cannot discard card - it can be placed on the board!")
                
                #raise ValueError("CANNOT_DISCARD_PLAYABLE_CARD")
            else:
                logger.info(f"Player {self.currentPlayer.getName()} discarded card - no valid placement was found")
                #logger.debug("Card cannot be placed anywhere - discarding according to official rules...")
                self.discardCurrentCard()
                if not self.cardsDeck:
                    self.endGame()
        
        elif self.turnPhase == 2:
            logger.info(f"Player {self.currentPlayer.getName()} skipped meeple placement")
            logger.debug("Finalizing turn...")

            for structure in self.structures:
                structure.checkCompletion()
                if structure.getIsCompleted():
                    self.scoreStructure(structure)

            self.nextTurn()
            self.turnPhase = 1
            
    def playFigure(self, player, x, y, position):
        """
        Places a figure on a valid card position
        """
        logger.debug("Playing figure...")

        card = self.gameBoard.getCard(x, y)
        if card != self.lastPlacedCard:
            #logger.info(f"{player.getName()}: Cannot place meeple here - only on the card you just placed")
            logger.debug(f"Player {player.getName()} was unable to play figure on card {self.gameBoard.getCard(x,y)} at [{x},{y}], can only place figures on last played card")
            
            if self.onShowNotification and not player.getIsAI():
                self.onShowNotification("error", "Cannot place meeple here - only on the card you just placed!")
            
            return False

        if not card:
            logger.debug(f"Player {player.getName()} was unable to place their meeple at [{x},{y}], no card was found.")
            #logger.debug(f"Unable to play figure, no card detected in selected space: {x};{y}")
            
            if self.onShowNotification and not player.getIsAI():
                self.onShowNotification("error", "No card found at this position!")
            
            return False

        # Find structure that this figure would be placed on
        structure = self.structureMap.get((x, y, position))
        if structure:
            if structure.figures:
                logger.debug(f"Player {player.getName()} was unable to place their meeple at [{x},{y}], position {position}, the structure is already occupied")
                #logger.debug(f"Unable to play figure, structure already claimed.")
                
                if self.onShowNotification and not player.getIsAI():
                    self.onShowNotification("error", "Cannot place meeple - this structure is already occupied!")
                
                return False

        # Attempt to place figure from player
        if player.figures:
            figure = player.getFigure()
            if figure.place(card, position):
                self.placedFigures.append(figure)
                logger.info(f"{player.getName()} placed a meeple on {position} position at [{x},{y}]")
                #logger.debug(f"{player.getName()} placed a figure at ({x}, {y}) on position {position}")

                if structure:
                    structure.addFigure(figure)

                logger.debug("Figure played")
                return True
            else:
                player.addFigure(figure)

        logger.debug(f"Player {player.getName()} was unable to place their meeple, player has no meeples left")
        #logger.debug("Unable to place figure, player has no figures left.")
        
        if self.onShowNotification and not player.getIsAI():
            self.onShowNotification("error", "No meeples left to place!")
        
        return False
            
    def detectStructures(self):
        """
        Updates structures based only on the last placed card.

        This version does not clear the whole structure list. Instead, it checks 
        only the newly placed card and updates or merges structures as needed.
        """
        logger.debug("Updating structures based on the last placed card...")

        if not self.lastPlacedCard:
            logger.debug("No card was placed. Skipping structure detection.")
            return

        position = self.gameBoard.getCardPosition(self.lastPlacedCard)
        if not position:
            logger.debug("Last placed card position not found.")
            return

        x, y = position
        self.visited = set()  # Reset visited only for the scope of this update

        for direction, terrainType in self.lastPlacedCard.getTerrains().items():
            key = (x, y, direction)

            if not terrainType or key in self.structureMap:
                continue

            # Step 1: Flood scan to get all connected sides
            connected_sides = self.scanConnectedSides(x, y, direction, terrainType)
            connected_structures = {self.structureMap.get(side) for side in connected_sides if self.structureMap.get(side)}
            connected_structures.discard(None)

            if connected_structures:
                # Merge all into one
                mainStructure = connected_structures.pop()
                for s in connected_structures:
                    mainStructure.merge(s)
                    self.structures.remove(s)
            else:
                mainStructure = Structure(terrainType.capitalize())
                self.structures.append(mainStructure)

            # Step 2: Assign all scanned sides to mainStructure
            for cx, cy, cdir in connected_sides:
                self.structureMap[(cx, cy, cdir)] = mainStructure
                mainStructure.addCardSide(self.gameBoard.getCard(cx, cy), cdir)
                
    def findConnectedStructures(self, x, y, direction, terrainType, structureMap):
        """
        Finds existing structures connected to the given card side

        Looks in the direction specified and checks neighboring tiles for a structure
        with matching terrain type. Used to determine whether to merge with existing
        structures or start a new one
        :param x: X-coordinate of the current card
        :param y: Y-coordinate of the current card
        :param direction: Direction being analyzed
        :param terrainType: The terrain type to match (e.g., 'city')
        :param structureMap: A dictionary mapping (x, y, direction) to existing structures
        :return: List of unique connected structures
        """

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
        return list(set(connected))  # Remove duplicates
        
    def scanConnectedSides(self, x, y, direction, terrainType):
        """
        Performs a pre-merge scan to collect all connected sides forming a continuous structure

        Traverses both internal (same-card) and external (neighboring-card) connections
        starting from a given card side, and gathers all (x, y, direction) segments
        that share the same terrain type. This method does not modify structureMap or
        the structure itself — it only returns all segments that belong together and
        should be associated with the same structure.

        Used before assigning or merging structures to ensure each segment is processed only once.

        :param x: X-coordinate of the starting card
        :param y: Y-coordinate of the starting card
        :param direction: Starting direction to explore from
        :param terrainType: The terrain type to match (e.g., 'city', 'road')
        :return: A set of (x, y, direction) tuples representing the entire connected structure
        """
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

            # Same-card connections
            connectedDirs = card.getConnections().get(cdir, []) if card.getConnections() else []
            for dir2 in connectedDirs:
                if (cx, cy, dir2) not in visited:
                    stack.append((cx, cy, dir2))

            # Neighbor connections
            neighbors = {
                "N": (cx, cy - 1, "S"),
                "S": (cx, cy + 1, "N"),
                "E": (cx + 1, cy, "W"),
                "W": (cx - 1, cy, "E")
            }
            
            if terrainType == "field":
                # Same-edge field adjacency (e.g., two north edges side-by-side)
                edgeLineAdjacents = {
                    "N": [((cx - 1, cy), "N"), ((cx + 1, cy), "N")],  # horizontal line
                    "S": [((cx - 1, cy), "S"), ((cx + 1, cy), "S")],
                    "E": [((cx, cy - 1), "E"), ((cx, cy + 1), "E")],  # vertical line
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
       
    def scoreStructure(self, structure):
        """
        Scores a completed structure by awarding points to the majority owner(s).
        """
        if not structure.getIsCompleted() and not self.gameOver:
            logger.debug("Structure is not completed, skipping scoring.")
            return

        score = structure.getScore(gameSession=self)
        owners = structure.getMajorityOwners()

        if not owners:
            logger.scoring(f"{structure.structureType} was completed but there were no meeples to score")
            #logger.debug("No figures on structure. No points awarded.")
            return

        logger.info(f"{structure.structureType} was completed")
        #logger.debug(f"Scoring structure: {structure.structureType} for {score} points.")
        
        for owner in owners:
            logger.scoring(f"Player {owner.getName()} scored {score} points from the {structure.structureType}")
            #logger.debug(f" - {owner.getName()} receives {score} points.")
            owner.addScore(score)

        structure.setColor(owners[0].getColorWithAlpha())
        
        for figure in structure.getFigures()[:]:
            structure.removeFigure(figure)
            figure.owner.addFigure(figure)
            logger.info(f"{figure.owner.getName()}'s meeple was returned")
            
    def endGame(self):
        logger.info("GAME OVER - No more cards in deck!")
        logger.scoring("Remaining incomplete structures will now be scored...")
        logger.debug("=== END OF GAME TRIGGERED ===")

        self.gameOver = True

        for structure in self.structures:
            if not structure.getIsCompleted():
                logger.scoring(f"Scoring incomplete {structure.structureType}...")
                self.scoreStructure(structure)

        logger.debug("All meeples have been returned to players")
        self.placedFigures.clear()
        self.showFinalResults()

        if self.onTurnEnded:
            self.onTurnEnded()
        
    def showFinalResults(self):
        logger.scoring("=== FINAL SCORES ===")
        
        sortedPlayers = sorted(self.players, key=lambda p: p.getScore(), reverse=True)
        
        for i, player in enumerate(sortedPlayers):
            if i == 0:
                logger.scoring(f"WINNER: {player.getName()}: {player.getScore()} points")
            else:
                logger.scoring(f"{player.getName()}: {player.getScore()} points")
            
    def getCandidatePositions(self):
        """
        Get all candidate positions where a card could potentially be placed
        (empty positions adjacent to existing cards)
        :return: Set of (x, y) tuples representing candidate positions
        """
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
                            if not self.gameBoard.getCard(nx, ny):  # Prázdné místo
                                candidatePositions.add((nx, ny))
        
        return candidatePositions

    def canPlaceCardAnywhere(self, card):
        """
        Check if card can be placed anywhere on the board using efficient candidate position search
        :param card: Card to check for placement
        :return: True if card can be placed somewhere, False otherwise
        """
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
                        logger.debug(f"Card can be placed at ({x}, {y}) with rotation {card.rotation}°")
                        return True
                    card.rotate()
            
            logger.debug("Card cannot be placed at any candidate position")
            return False
            
        finally:
            while card.rotation != originalRotation:
                card.rotate()
                
    def getRandomValidPlacement(self, card):
        """
        Get a random valid placement for the given card
        :param card: Card to place
        :return: (x, y, rotations_needed) or None if no placement possible
        """
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
            
    def serialize(self):
        logger.debug("Serializing game state")
        return {
            "players": [player.serialize() for player in self.players],
            "deck": [card.serialize() for card in self.cardsDeck],
            "board": self.gameBoard.serialize(),
            "current_card": self.currentCard.serialize() if self.currentCard else None,
            "last_placed_card": self.lastPlacedCard.serialize() if self.lastPlacedCard else None,
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
            "structure_map": list(self.structureMap.keys()),  # keys only; optional
            "structures": [s.serialize() for s in self.structures if hasattr(s, 'serialize')],
            "game_mode": self.gameMode
        }
        
    @classmethod
    def deserialize(cls, data):
        # Rebuild player list
        players = []
        for p in data.get("players", []):
            try:
                if p["name"].startswith("AI_"):
                    players.append(AIPlayer.deserialize(p))
                else:
                    players.append(Player.deserialize(p))
            except Exception as e:
                logger.warning(f"Skipping malformed player entry: {p} - {e}")

        session = cls([p.getName() for p in players], noInit=True)
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
            logger.warning(f"Failed to deserialize current_card - {e}")
            session.currentCard = None

        try:
            session.lastPlacedCard = Card.deserialize(data["last_placed_card"]) if data.get("last_placed_card") else None
        except Exception as e:
            logger.warning(f"Failed to deserialize last_placed_card - {e}")
            session.lastPlacedCard = None

        try:
            session.gameBoard = GameBoard.deserialize(data.get("board", {}))
        except Exception as e:
            logger.warning(f"Failed to deserialize gameBoard - {e}")
            session.gameBoard = GameBoard()

        try:
            session.isFirstRound = bool(data.get("is_first_round", True))
            session.turnPhase = int(data.get("turn_phase", 1))
            session.gameOver = bool(data.get("game_over", False))
        except Exception as e:
            logger.warning(f"Failed to parse basic session attributes - {e}")

        session.gameMode = data.get("game_mode", None)

        # Placed Figures
        playerMap = {p.getIndex(): p for p in session.players}
        session.placedFigures = []
        for fdata in data.get("placed_figures", []):
            try:
                figure = Figure.deserialize(fdata, playerMap, session.gameBoard)
                if figure:
                    session.placedFigures.append(figure)
            except Exception as e:
                logger.warning(f"Skipping malformed figure: {fdata} - {e}")
                
        # Structures
        session.structures = []
        for s in data.get("structures", []):
            try:
                structure = Structure.deserialize(s, session.gameBoard, playerMap, session.placedFigures)
                if structure:
                    session.structures.append(structure)
            except Exception as e:
                logger.warning(f"Skipping malformed structure: {s} - {e}")
                
        # Rebuild structureMap from structures to avoid overlap/duplication
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

        # Re-link structure figures to placedFigures instances
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
