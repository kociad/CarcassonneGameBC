from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
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
        self.structures = [] # Currently unused
        self.gameMode = None # Currently unused
        self.currentCard = None # Currently selected card
        self.isFirstRound = True # Is this the first (automatic) round?
        
        # Create a list of players
        self.generatePlayerList(playerNames)
        
        # Generate new card deck based on specified definitions and distributions
        self.cardsDeck = self.generateCardsDeck()
        
        # Shuffle the new deck
        self.shuffleCardsDeck(self.cardsDeck)
                
        # Automatically place the starting card
        self.placeStartingCard()
        
    def generatePlayerList(self, playerNames):
        """
        Generates a list of indexed players for the game
        :param playerNames: A list of player names
        """
        print(f"Generating a list of players...")
        if playerNames:
            index = 0
            
            for player in playerNames:
                self.players.append(Player(player, index))
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
            {"image": "Base_Game_C3_Tile_A.png", "terrain": {"N": "field", "E": "field", "S": "road", "W": "field"}},
            {"image": "Base_Game_C3_Tile_B.png", "terrain": {"N": "field", "E": "field", "S": "field", "W": "field"}},
            {"image": "Base_Game_C3_Tile_C.png", "terrain": {"N": "city", "E": "city", "S": "city", "W": "city"}},
            {"image": "Base_Game_C3_Tile_D.png", "terrain": {"N": "city", "E": "road", "S": "field", "W": "road"}},
            {"image": "Base_Game_C3_Tile_E.png", "terrain": {"N": "city", "E": "field", "S": "field", "W": "field"}},
            {"image": "Base_Game_C3_Tile_F.png", "terrain": {"N": "field", "E": "city", "S": "field", "W": "city"}},
            {"image": "Base_Game_C3_Tile_G.png", "terrain": {"N": "field", "E": "city", "S": "field", "W": "city"}},
            {"image": "Base_Game_C3_Tile_H.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_I.png", "terrain": {"N": "city", "E": "field", "S": "field", "W": "city"}},
            {"image": "Base_Game_C3_Tile_J.png", "terrain": {"N": "city", "E": "road", "S": "road", "W": "field"}},
            {"image": "Base_Game_C3_Tile_K.png", "terrain": {"N": "city", "E": "field", "S": "road", "W": "road"}},
            {"image": "Base_Game_C3_Tile_L.png", "terrain": {"N": "city", "E": "road", "S": "road", "W": "road"}},
            {"image": "Base_Game_C3_Tile_M.png", "terrain": {"N": "city", "E": "city", "S": "field", "W": "field"}},
            {"image": "Base_Game_C3_Tile_N.png", "terrain": {"N": "city", "E": "city", "S": "field", "W": "field"}},
            {"image": "Base_Game_C3_Tile_O.png", "terrain": {"N": "city", "E": "road", "S": "road", "W": "city"}},
            {"image": "Base_Game_C3_Tile_P.png", "terrain": {"N": "city", "E": "road", "S": "road", "W": "city"}},
            {"image": "Base_Game_C3_Tile_Q.png", "terrain": {"N": "city", "E": "city", "S": "field", "W": "city"}},
            {"image": "Base_Game_C3_Tile_R.png", "terrain": {"N": "city", "E": "city", "S": "field", "W": "city"}},
            {"image": "Base_Game_C3_Tile_S.png", "terrain": {"N": "city", "E": "city", "S": "road", "W": "city"}},
            {"image": "Base_Game_C3_Tile_T.png", "terrain": {"N": "city", "E": "city", "S": "road", "W": "city"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "road", "E": "field", "S": "road", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "field", "E": "field", "S": "road", "W": "road"}},
            {"image": "Base_Game_C3_Tile_W.png", "terrain": {"N": "field", "E": "road", "S": "road", "W": "road"}},
            {"image": "Base_Game_C3_Tile_X.png", "terrain": {"N": "road", "E": "road", "S": "road", "W": "road"}}
            
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
            terrain = card["terrain"]
            count = card_distributions.get(image, 1)  # Default to 1 if not listed in distributions
            cards.extend([Card(TILE_IMAGES_PATH + image, terrain) for card in range(count)])
            
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
            print("Unable to play first , no cardsDeck available")
    
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
    
    def placeCard(self, card, x, y):
        """
        Places a card on the board without validation.
        :param card: The card to be placed.
        :param x: X-coordinate on the board.
        :param y: Y-coordinate on the board.
        """
        print("Placing card...")
        self.gameBoard.placeCard(card, x, y)
        print("Card placed")
    
    def nextTurn(self):
        """
        Moves to the next player's turn.
        """
        if not self.isFirstRound:
            print("Advancing player turn...")
            currentIndex = self.currentPlayer.index
            nextIndex = (currentIndex + 1) % len(self.players)
            print(f"Current player {self.currentPlayer.name} index - {currentIndex} (out of {len(self.players) - 1})")
            for player in self.players:
                if player.index == nextIndex:
                    self.currentPlayer = player
                    break
            print(f"New player self {self.currentPlayer.name} index - {self.currentPlayer.index} (out of {len(self.players) - 1})")
        self.currentCard = self.drawCard()

    def getCurrentPlayer(self): # Also not working
        """
        Retrieves the current player's turn.
        :return: Player object representing the current player.
        """
        return self.players[0]
        
    def getCurrentCard(self): # Not working
        """
        Retrieves the current card.
        :return: Card object representing the current card.
        """
        return self.cardsDeck[0]
        
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
            
        self.placeCard(card, x, y)
        self.currentCard = None
        
        print ("Card played")
        
        self.nextTurn()
        
        return True
        
    def discardCurrentCard (self):
        """
        Discards current selected card and selects a new one
        """
        if self.currentCard:
            self.currentCard = self.drawCard()
        
    def playMeeple (self):
        pass
        
    def playTurn(self, x, y, player=None):
        pass
        
    def listPlayers(self): # Debug purposes only
        """
        Print a list of all players in the game with their info
        """
        print("Printing player info...")
        for player in self.players:
            print(f"Name: {player.name}")
            print(f"Score: {player.score}")
            print(f"Index: {player.index}")
            print(f"Figures: {player.figures}")
