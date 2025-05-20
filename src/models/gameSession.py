import random
import logging

from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from models.structure import Structure
from models.aiPlayer import AIPlayer
from settings import TILE_IMAGES_PATH, DEBUG

logger = logging.getLogger(__name__)

class GameSession:
    """
    Manages the overall game state, including players, board, and card placement.
    """
    
    def __init__(self, playerNames):
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
        
        # Create a list of players
        self.generatePlayerList(playerNames)
        
        # Generate new card deck based on specified definitions and distributions
        self.cardsDeck = self.generateCardsDeck()
        
        # Shuffle the new deck
        self.shuffleCardsDeck(self.cardsDeck)
                
        # Automatically place the starting card
        #self.placeStartingCard()
        
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
        
    def setOnTurnEnded(self, onTurnEnded):
        self.onTurnEnded = onTurnEnded
        
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
            cards.extend([Card(TILE_IMAGES_PATH + image, terrains, connections, features) for card in range(count)])
            
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
                    
            logger.debug(f"New player {self.currentPlayer.getName()} index - {self.currentPlayer.getIndex()} (out of {len(self.players) - 1})")
            
            self.currentCard = self.drawCard()
            self.turnPhase = 1  # Reset for next player
            logger.debug("Calling nextTurn()")
            if self.onTurnEnded:
                logger.debug("Calling onTurnEnded() callback")
                self.onTurnEnded()
        else:
            self.endGame()
        
    def playCard (self, x, y):
        """
        Plays the card placing part of the turn
        :param x: X-coordinate of the selected space
        :param y: Y-coordinate of the selected space
        """
        logger.debug("Playing card...")
        card = self.currentCard
        
        if not card:
            if not self.cardsDeck:
                logger.debug("Unable to play turn, no card is selected and no cardsDeck is available")
                return False
            card = self.drawCard()
        
        if not self.gameBoard.validateCardPlacement(card, x, y) and not self.isFirstRound:
            logger.debug(f"Unable to place card, placement is invalid, validateCardPlacement {self.gameBoard.validateCardPlacement(card, x, y)}, isFirstRound {self.isFirstRound}")
            return False
            
        self.gameBoard.placeCard(card, x, y)
        self.lastPlacedCard = card
        self.currentCard = None
        
        logger.debug (f"Card played, last played card set to card {card} at {x};{y}")
        
        self.detectStructures() # Structuremap needs to be updated after every card placement
        
        """
        if self.isFirstRound:
            self.nextTurn()
        """
        
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
        Skips the current phase action:
        - Phase 1: Discards the current card and draws a new one.
        - Phase 2: Skips figure placement, finalizes the turn.
        """
        if self.turnPhase == 1:
            logger.debug("Skipping card placement. Drawing new card...")
            self.discardCurrentCard()
            if not self.cardsDeck:
                self.endGame()
        
        elif self.turnPhase == 2:
            logger.debug("Skipping figure placement. Finalizing turn...")

            #self.detectStructures()

            logger.debug("Checking completed structures...")
            for structure in self.structures:
                structure.checkCompletion()
                if structure.getIsCompleted():
                    logger.debug(f"Structure {structure.structureType} is completed!")
                    self.scoreStructure(structure)

            self.nextTurn()
            self.turnPhase = 1
            
    def playFigure(self, player, x, y, position):
        """
        Places a figure on a valid card position
        :param player: The player placing the figure
        :param x: X-coordinate on the board
        :param y: Y-coordinate on the board
        :param position: The position on the card (N, W, S, E, etc.)
        :return: True if placement is successful, False otherwise
        """
        logger.debug("Playing figure...")

        card = self.gameBoard.getCard(x, y)
        if card != self.lastPlacedCard:
            logger.debug("Unable to play figure, can only place figures on last played card")
            return False

        if not card:
            logger.debug(f"Unable to play figure, no card detected in selected space: {x};{y}")
            return False

        # Find structure that this figure would be placed on
        structure = self.structureMap.get((x, y, position))
        if structure:
            if structure.figures:
                logger.debug(f"Unable to play figure, structure already claimed.")
                return False  # Structure is already claimed

        # Attempt to place figure from player
        if player.figures:
            figure = player.getFigure()
            if figure.place(card, position):
                self.placedFigures.append(figure)
                logger.debug(f"{player.getName()} placed a figure at ({x}, {y}) on position {position}")

                if structure:
                    structure.addFigure(figure)

                logger.debug("Figure played")
                #self.nextTurn()
                return True
            else:
                player.addFigure(figure)  # Return figure if placement failed

        logger.debug("Unable to place figure, player has no figures left.")
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
        Removes their figures afterward (Step 13).
        :param structure: The completed Structure to score.
        """
        if not structure.getIsCompleted() and not self.gameOver:
            logger.debug("Structure is not completed, skipping scoring.")
            return

        score = structure.getScore(gameSession=self)
        owners = structure.getMajorityOwners()

        if not owners:
            logger.debug("No figures on structure. No points awarded.")
            return

        logger.debug(f"Scoring structure: {structure.structureType} for {score} points.")
        for owner in owners:
            logger.debug(f" - {owner.getName()} receives {score} points.")
            owner.addScore(score)

        # Set structure color to owner player
        structure.setColor(owners[0].getColorWithAlpha())
        
        # Remove figures after scoring and return them to players
        logger.debug(f"Figures to be removed: {structure.getFigures()}")
        for figure in structure.getFigures()[:]:
            structure.removeFigure(figure)
            figure.owner.addFigure(figure)
            
    def endGame(self):
        logger.debug("=== END OF GAME TRIGGERED ===")
        logger.debug("Scoring all remaining incomplete structures...")
        
        self.gameOver = True

        for structure in self.structures:
            if not structure.getIsCompleted():
                logger.debug(f"- Incomplete {structure.structureType} scored...")
                self.scoreStructure(structure)

        logger.debug("All structures scored. Returning all figures...")
        self.placedFigures.clear()  # All figures should already be returned during scoring

        self.showFinalResults()
        
    def showFinalResults(self):
        logger.info("\n=== FINAL SCORES ===")
        for player in self.players:
            logger.info(f"{player.getName()}: {player.getScore()} points")
            
    def serialize(self):
        logger.info("Serializing game state")
        return {
            "players": [player.serialize() for player in self.players],
            "deck": [card.serialize() for card in self.cardsDeck],
            "board": self.gameBoard.serialize(),
            "current_card": self.currentCard.serialize() if self.currentCard else None,
            "last_placed_card": self.lastPlacedCard.serialize() if self.lastPlacedCard else None,
            "is_first_round": self.isFirstRound,
            "turn_phase": self.turnPhase,
            "placed_figures": [
                {
                    **figure.serialize(),
                    "card_position": self.gameBoard.getCardPosition(figure.card)
                }
                for figure in self.placedFigures if figure.card
            ],
            "current_player_index": self.currentPlayer.getIndex(),
            "game_over": self.gameOver
        }
        
    @classmethod
    def deserialize(cls, data):
        from models.player import Player
        from models.aiPlayer import AIPlayer
        from models.card import Card
        from models.gameBoard import GameBoard
        from models.figure import Figure  # Assuming figures are serializable
        from models.structure import Structure  # Optional, for post-sync structure recovery

        # Rebuild player list
        players = []
        for p in data["players"]:
            if p["name"].startswith("AI_"):
                players.append(AIPlayer.deserialize(p))
            else:
                players.append(Player.deserialize(p))

        # Initialize with player names only
        session = cls([p.getName() for p in players])
        session.players = players

        # Restore current player
        session.currentPlayer = players[data["current_player_index"]]

        # Rebuild deck
        session.cardsDeck = [Card.deserialize(c) for c in data["deck"]]

        # Rebuild current/last cards
        session.currentCard = Card.deserialize(data["current_card"]) if data["current_card"] else None
        session.lastPlacedCard = Card.deserialize(data["last_placed_card"]) if data["last_placed_card"] else None

        # Board
        session.gameBoard = GameBoard.deserialize(data["board"])

        # Game flags
        session.isFirstRound = data["is_first_round"]
        session.turnPhase = data["turn_phase"]
        session.gameOver = data["game_over"]

        # Placed figures (if needed)
        # Build player map for figure deserialization
        playerMap = {p.getIndex(): p for p in session.players}

        # Restore placed figures
        session.placedFigures = [
            Figure.deserialize(fdata, playerMap, session.gameBoard)
            for fdata in data.get("placed_figures", [])
        ]
        
        return session
