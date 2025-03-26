from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from models.structure import Structure
from settings import TILE_IMAGES_PATH
import random
#from models.structure import Structure

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
        
        # Create a list of players
        self.generatePlayerList(playerNames)
        
        # Generate new card deck based on specified definitions and distributions
        self.cardsDeck = self.generateCardsDeck()
        
        # Shuffle the new deck
        self.shuffleCardsDeck(self.cardsDeck)
                
        # Automatically place the starting card
        self.placeStartingCard()
        
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
        
    def generatePlayerList(self, playerNames):
        """
        Generates a list of indexed players for the game
        :param playerNames: A list of player names
        """
        print(f"Generating a list of players...")
        
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
                self.players.append(Player(player, index, colors.pop()))
                index = index + 1
            
            self.currentPlayer=self.players[0]
        print(f"Player list generated")
        self.listPlayers()
        
    def generateCardsDeck(self):
        """
        Generates a deck of cards for the game.
        :return: A list of Card objects representing the card deck.
        """
        print("Generating deck...")
        
        card_definitions = [
            {"image": "Base_Game_C3_Tile_A.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "field", "C": "monastery"}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}},
            {"image": "Base_Game_C3_Tile_B.png", "terrains": {"N": "field", "E": "field", "S": "field", "W": "field", "C": "monastery"}, "connections":{"N":["E","S","W"],"E":["S","W","N"],"S":["W","N","E"],"W":["N","E","S"]}},
            {"image": "Base_Game_C3_Tile_C.png", "terrains": {"N": "city", "E": "city", "S": "city", "W": "city", "C": None}, "connections":{"N":["E","S","W"],"E":["S","W","N"],"S":["W","N","E"],"W":["N","E","S"]}},
            {"image": "Base_Game_C3_Tile_D.png", "terrains": {"N": "city", "E": "road", "S": "field", "W": "road", "C": None}, "connections":{"E":["W"], "W":["E"]}},
            {"image": "Base_Game_C3_Tile_E.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "field", "C": None}, "connections":{"E":["S","W"],"S":["W","E"],"W":["E","S"]}},
            {"image": "Base_Game_C3_Tile_F.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"E":["W"],"W":["E"]}},
            {"image": "Base_Game_C3_Tile_G.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"E":["W"],"W":["E"]}},
            {"image": "Base_Game_C3_Tile_H.png", "terrains": {"N": "city", "E": "field", "S": "city", "W": "field", "C": None}, "connections":{"E":["W"],"W":["E"]}},
            {"image": "Base_Game_C3_Tile_I.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "city", "C": None}, "connections":{"E":["S"],"S":["E"]}},
            {"image": "Base_Game_C3_Tile_J.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "field", "C": None}, "connections":{"E":["S"],"S":["E"]}},
            {"image": "Base_Game_C3_Tile_K.png", "terrains": {"N": "city", "E": "field", "S": "road", "W": "road", "C": None}, "connections":{"S":["W"],"W":["S"]}},
            {"image": "Base_Game_C3_Tile_L.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None},
            {"image": "Base_Game_C3_Tile_M.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections":{"N":["E"],"E":["N"],"S":["W"],"W":["S"]}},
            {"image": "Base_Game_C3_Tile_N.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections":{"N":["E"],"E":["N"],"S":["W"],"W":["S"]}},
            {"image": "Base_Game_C3_Tile_O.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections":{"N":["W"],"E":["S"],"S":["E"],"W":["N"]}},
            {"image": "Base_Game_C3_Tile_P.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections":{"N":["W"],"E":["S"],"S":["E"],"W":["N"]}},
            {"image": "Base_Game_C3_Tile_Q.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}},
            {"image": "Base_Game_C3_Tile_R.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}},
            {"image": "Base_Game_C3_Tile_S.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}},
            {"image": "Base_Game_C3_Tile_T.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections":{"N":["E","W"],"E":["W","N"],"W":["N","E"]}},
            {"image": "Base_Game_C3_Tile_U.png", "terrains": {"N": "road", "E": "field", "S": "road", "W": "field", "C": None}, "connections":{"N":["S"],"S":["N"]}},
            {"image": "Base_Game_C3_Tile_V.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "road", "C": None}, "connections":{"N":["E"],"E":["N"],"S":["W"],"W":["S"]}},
            {"image": "Base_Game_C3_Tile_W.png", "terrains": {"N": "field", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None},
            {"image": "Base_Game_C3_Tile_X.png", "terrains": {"N": "road", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None}
            
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
            count = card_distributions.get(image, 1)  # Default to 1 if not listed in distributions
            cards.extend([Card(TILE_IMAGES_PATH + image, terrains, connections) for card in range(count)])
            
        print("Deck generated")
        return cards
        
    def shuffleCardsDeck(self, deck):
        """
        Shuffles an existing deck of cards
        :param deck: Existing card deck
        :return: Shuffled deck
        """
        print("Shuffling deck...")
        
        random.shuffle(deck)
        
        print("Deck shuffled")
    
    def placeStartingCard(self):
        """
        Plays the first turn automatically (places first card)
        """
        print("Playing first turn...")
        center_x, center_y = self.gameBoard.getCenterPosition()
        if self.cardsDeck:
            if self.playCard(center_x,center_y):
                self.isFirstRound = False
                print("First turn played")
        else:
            print("Unable to play first round, no cardsDeck available")
    
    def drawCard(self):
        """
        Draws a card from the deck for the current player.
        :return: The drawn card if available, otherwise None.
        """
        print("Drawing card...")
        if self.cardsDeck:
            print("Card drawn")
            return self.cardsDeck.pop(0)
            
        return None
    
    def nextTurn(self):
        """
        Moves to the next player's turn.
        """
        if not self.isFirstRound:
            print("Advancing player turn...")
            currentIndex = self.currentPlayer.index
            nextIndex = (currentIndex + 1) % len(self.players)
            #print(f"Current player {self.currentPlayer.name} index - {currentIndex} (out of {len(self.players) - 1})")
            for player in self.players:
                if player.index == nextIndex:
                    self.currentPlayer = player
                    break
            print(f"New player {self.currentPlayer.getName()} index - {self.currentPlayer.getIndex()} (out of {len(self.players) - 1})")
        self.currentCard = self.drawCard()
        
    def playCard (self, x, y):
        """
        Plays the card placing part of the turn
        :param x: X-coordinate of the selected space
        :param y: Y-coordinate of the selected space
        """
        print("Playing card...")
        card = self.currentCard
        
        if not card:
            if not self.cardsDeck:
                print("Unable to play turn, no card is selected and no cardsDeck is available")
                return False
            card = self.drawCard()
        
        if not self.gameBoard.validateCardPlacement(card, x, y) and not self.isFirstRound:
            print(f"Unable to place card, placement is invalid, validateCardPlacement {self.gameBoard.validateCardPlacement(card, x, y)}, isFirstRound {self.isFirstRound}")
            return False
            
        self.gameBoard.placeCard(card, x, y)
        self.lastPlacedCard = card
        self.currentCard = None
        
        print (f"Card played, last played card set to card {card} at {x};{y}")
        
        if self.isFirstRound:
            self.nextTurn()
        
        return True
        
    def discardCurrentCard (self):
        """
        Discards current selected card and selects a new one
        """
        if self.currentCard:
            self.currentCard = self.drawCard()
        
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
            print("Turn Phase 1: Attempting to place card...")
            if self.playCard(x, y):
                self.turnPhase = 2  # Move to figure placement phase
            else:
                print("Card placement failed.")
                
            self.detectStructures() # Structure detection needs to be performed after each action
            
            return  # Wait for next player click (figure phase or retry)

        # Phase 2: Place Figure
        elif self.turnPhase == 2:
            print("Turn Phase 2: Attempting to place figure...")

            if self.playFigure(player, x, y, position):  # Defaulting to center — position must be set properly by event handler
                print("Figure placed.")
            else:
                print("Figure not placed or skipped.")
                return # Wait for next player action (retry figure placement or skip)

            self.detectStructures() # Structure detection needs to be performed after each action

            print("Checking completed structures...")
            for structure in self.structures:
                if structure.checkCompletion():
                    print(f"Structure {structure.structureType} is completed!")
                    # TODO: Award points, remove figures, etc.

            self.nextTurn()
            self.turnPhase = 1  # Reset for next player
            
    def skipCurrentAction(self):
        """
        Skips the current phase action:
        - Phase 1: Discards the current card and draws a new one.
        - Phase 2: Skips figure placement, finalizes the turn.
        """
        if self.turnPhase == 1:
            print("Skipping card placement. Drawing new card...")
            self.discardCurrentCard()
        
        elif self.turnPhase == 2:
            print("Skipping figure placement. Finalizing turn...")

            self.detectStructures()

            print("Checking completed structures...")
            for structure in self.structures:
                if structure.checkCompletion():
                    print(f"Structure {structure.structureType} is completed!")
                    # TODO: Award points, remove figures, etc.

            self.nextTurn()
            self.turnPhase = 1
            
    def listPlayers(self): # Debug purposes only
        """
        Print a list of all players in the game with their info
        """
        print("Printing player info...")
        for player in self.players:
            print(f"Name: {player.getName()}")
            print(f"Score: {player.getScore()}")
            print(f"Index: {player.getIndex()}")
            print(f"Figures: {player.getFigures()}")
            
    def playFigure(self, player, x, y, position):
        """
        Places a figure on a valid card position
        :param player: The player placing the figure
        :param x: X-coordinate on the board
        :param y: Y-coordinate on the board
        :param position: The position on the card (N, W, S, E, etc.)
        :return: True if placement is successful, False otherwise
        """
        print("Playing figure...")

        card = self.gameBoard.getCard(x, y)
        if card != self.lastPlacedCard:
            print("Unable to play figure, can only place figures on last played card")
            return False

        if not card:
            print(f"Unable to play figure, no card detected in selected space: {x};{y}")
            return False

        # Find structure that this figure would be placed on
        structure = self.structureMap.get((x, y, position))
        if structure:
            if structure.figures:
                print(f"Unable to play figure, structure already claimed by {structure.getFigureOwner().getName()}")
                return False  # Structure is already claimed

        # Attempt to place figure from player
        if player.figures:
            figure = player.getFigure()
            if figure.place(card, position):
                self.placedFigures.append(figure)
                print(f"{player.getName()} placed a figure at ({x}, {y}) on position {position}")

                if structure:
                    structure.addFigure(figure)

                print("Figure played")
                self.nextTurn()
                return True
            else:
                player.addFigure(figure)  # Return figure if placement failed

        print("Unable to place figure, player has no figures left.")
        return False
            
    def detectStructures(self):
        """
        Updates structures based only on the last placed card.

        This version does not clear the whole structure list. Instead, it checks 
        only the newly placed card and updates or merges structures as needed.
        """
        print("Updating structures based on the last placed card...")

        if not self.lastPlacedCard:
            print("No card was placed. Skipping structure detection.")
            return

        position = self.gameBoard.getCardPosition(self.lastPlacedCard)
        if not position:
            print("Last placed card position not found.")
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
                    print(f"Existing structure detected at ({nx}, {ny}) {ndir}")
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

            if cdir in neighbors:
                nx, ny, ndir = neighbors[cdir]
                neighbor = self.gameBoard.getCard(nx, ny)
                if neighbor and neighbor.getTerrains().get(ndir) == terrainType:
                    stack.append((nx, ny, ndir))

        return visited
       

