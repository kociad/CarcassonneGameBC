from models.game_board import GameBoard
from models.card import Card
from models.player import Player
from settings import TILE_IMAGES_PATH
#from models.structure import Structure

class GameSession:
    """
    Manages the overall game state, including players, board, and tile placement.
    """
    
    def __init__(self, player_names):
        """
        Initializes the game session with players, board, and tile deck.
        :param player_names: List of player names to create Player instances.
        """
        self.board = GameBoard()
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0
        self.tile_deck = self.generate_tile_deck()
        
        # Automatically place the starting tile
        self.place_starting_tile()
    
    def generate_tile_deck(self):
        """
        Generates a deck of tiles for the game.
        :return: A list of Card objects representing the tile deck.
        """
        tile_definitions = [
            {"image": "Base_Game_C3_Tile_A.png", "terrain": {"N": "field", "E": "field", "S": "road", "W": "field"}},
            {"image": "Base_Game_C3_Tile_A.png", "terrain": {"N": "field", "E": "field", "S": "road", "W": "field"}},
            {"image": "Base_Game_C3_Tile_B.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_B.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_B.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_B.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_C.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_D.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_D.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_D.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_D.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_E.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_E.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_E.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_E.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_E.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_F.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_F.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_G.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_H.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_H.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_H.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_I.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_I.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_J.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_J.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_J.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_K.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_K.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_K.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_L.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_L.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_L.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_M.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_M.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_N.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_N.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_N.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_O.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_O.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_P.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_P.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_P.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_Q.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_R.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_R.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_R.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_S.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_S.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_T.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_U.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_V.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_W.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_W.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_W.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_W.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            {"image": "Base_Game_C3_Tile_X.png", "terrain": {"N": "city", "E": "field", "S": "city", "W": "field"}},
            
            # Add more tile definitions as needed...
        ]
        
        tiles = []
        
        for tile in tile_definitions:
            tiles.append(Card(TILE_IMAGES_PATH + tile["image"], tile["terrain"]))
            
        return tiles
    
    def place_starting_tile(self):
        """
        Draws and places the starting tile at the center of the board.
        """
        if self.tile_deck:
            starting_tile = self.tile_deck.pop(0)
            center_x, center_y = self.board.get_center_position()
            self.board.place_tile(starting_tile, center_x, center_y)
            print("Starting tile placed")
    
    def draw_tile(self):
        """
        Draws a tile from the deck for the current player.
        :return: The drawn tile if available, otherwise None.
        """
        if self.tile_deck:
            return self.tile_deck.pop(0)
        return None
    
    def place_tile(self, tile, x, y):
        """
        Places a tile on the board without validation.
        :param tile: The tile to be placed.
        :param x: X-coordinate on the board.
        :param y: Y-coordinate on the board.
        """
        self.board.place_tile(tile, x, y)
    
    def next_turn(self):
        """
        Moves to the next player's turn.
        """
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def get_current_player(self):
        """
        Retrieves the current player's turn.
        :return: Player object representing the current player.
        """
        return self.players[self.current_player_index]
