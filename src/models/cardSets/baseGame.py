"""
Base Game Card Set for Carcassonne
Contains all the standard tiles from the base game.
"""

CARD_SET_NAME = "Base Game"

CARD_DEFINITIONS = [
    {"image": "baseGame/Base_Game_C3_Tile_A.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "field", "C": "monastery"}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_B.png", "terrains": {"N": "field", "E": "field", "S": "field", "W": "field", "C": "monastery"}, "connections": {"N": ["E", "S", "W"], "E": ["S", "W", "N"], "S": ["W", "N", "E"], "W": ["N", "E", "S"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_C.png", "terrains": {"N": "city", "E": "city", "S": "city", "W": "city", "C": None}, "connections": {"N": ["E", "S", "W"], "E": ["S", "W", "N"], "S": ["W", "N", "E"], "W": ["N", "E", "S"]}, "features": ["coat"]},
    {"image": "baseGame/Base_Game_C3_Tile_D.png", "terrains": {"N": "city", "E": "road", "S": "field", "W": "road", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_E.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "field", "C": None}, "connections": {"E": ["S", "W"], "S": ["W", "E"], "W": ["E", "S"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_F.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": ["coat"]},
    {"image": "baseGame/Base_Game_C3_Tile_G.png", "terrains": {"N": "field", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_H.png", "terrains": {"N": "city", "E": "field", "S": "city", "W": "field", "C": None}, "connections": {"E": ["W"], "W": ["E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_I.png", "terrains": {"N": "city", "E": "field", "S": "field", "W": "city", "C": None}, "connections": {"E": ["S"], "S": ["E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_J.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "field", "C": None}, "connections": {"E": ["S"], "S": ["E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_K.png", "terrains": {"N": "city", "E": "field", "S": "road", "W": "road", "C": None}, "connections": {"S": ["W"], "W": ["S"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_L.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_M.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections": {"N": ["E"], "E": ["N"], "S": ["W"], "W": ["S"]}, "features": ["coat"]},
    {"image": "baseGame/Base_Game_C3_Tile_N.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "field", "C": None}, "connections": {"N": ["E"], "E": ["N"], "S": ["W"], "W": ["S"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_O.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections": {"N": ["W"], "E": ["S"], "S": ["E"], "W": ["N"]}, "features": ["coat"]},
    {"image": "baseGame/Base_Game_C3_Tile_P.png", "terrains": {"N": "city", "E": "road", "S": "road", "W": "city", "C": None}, "connections": {"N": ["W"], "E": ["S"], "S": ["E"], "W": ["N"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_Q.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": ["coat"]},
    {"image": "baseGame/Base_Game_C3_Tile_R.png", "terrains": {"N": "city", "E": "city", "S": "field", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_S.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": ["coat"]},
    {"image": "baseGame/Base_Game_C3_Tile_T.png", "terrains": {"N": "city", "E": "city", "S": "road", "W": "city", "C": None}, "connections": {"N": ["E", "W"], "E": ["W", "N"], "W": ["N", "E"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_U.png", "terrains": {"N": "road", "E": "field", "S": "road", "W": "field", "C": None}, "connections": {"N": ["S"], "S": ["N"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_V.png", "terrains": {"N": "field", "E": "field", "S": "road", "W": "road", "C": None}, "connections": {"N": ["E"], "E": ["N"], "S": ["W"], "W": ["S"]}, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_W.png", "terrains": {"N": "field", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None},
    {"image": "baseGame/Base_Game_C3_Tile_X.png", "terrains": {"N": "road", "E": "road", "S": "road", "W": "road", "C": None}, "connections": None, "features": None}
]

CARD_DISTRIBUTIONS = {
    "baseGame/Base_Game_C3_Tile_A.png": 2,
    "baseGame/Base_Game_C3_Tile_B.png": 4,
    "baseGame/Base_Game_C3_Tile_C.png": 1,
    "baseGame/Base_Game_C3_Tile_D.png": 4,
    "baseGame/Base_Game_C3_Tile_E.png": 5,
    "baseGame/Base_Game_C3_Tile_F.png": 2,
    "baseGame/Base_Game_C3_Tile_G.png": 1,
    "baseGame/Base_Game_C3_Tile_H.png": 3,
    "baseGame/Base_Game_C3_Tile_I.png": 2,
    "baseGame/Base_Game_C3_Tile_J.png": 3,
    "baseGame/Base_Game_C3_Tile_K.png": 3,
    "baseGame/Base_Game_C3_Tile_L.png": 3,
    "baseGame/Base_Game_C3_Tile_M.png": 2,
    "baseGame/Base_Game_C3_Tile_N.png": 3,
    "baseGame/Base_Game_C3_Tile_O.png": 2,
    "baseGame/Base_Game_C3_Tile_P.png": 3,
    "baseGame/Base_Game_C3_Tile_Q.png": 1,
    "baseGame/Base_Game_C3_Tile_R.png": 3,
    "baseGame/Base_Game_C3_Tile_S.png": 2,
    "baseGame/Base_Game_C3_Tile_T.png": 1,
    "baseGame/Base_Game_C3_Tile_U.png": 8,
    "baseGame/Base_Game_C3_Tile_V.png": 9,
    "baseGame/Base_Game_C3_Tile_W.png": 4,
    "baseGame/Base_Game_C3_Tile_X.png": 1
}

def getCardDefinitions():
    """Return the card definitions for the base game."""
    return CARD_DEFINITIONS

def getCardDistributions():
    """Return the card distributions for the base game."""
    return CARD_DISTRIBUTIONS 