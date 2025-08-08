"""
Base Game Card Set for Carcassonne
Contains all the standard tiles from the base game.
"""

CARD_SET_NAME = "Base Game (Center Test)"

CARD_DEFINITIONS = [{
    "image": "base_game/Base_Game_C3_Tile_A.png",
    "terrains": {
        "N": "field",
        "E": "field",
        "S": "road",
        "W": "field",
        "C": "monastery"
    },
    "connections": {
        "N": ["E", "W"],
        "E": ["W", "N"],
        "W": ["N", "E"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_B.png",
    "terrains": {
        "N": "field",
        "E": "field",
        "S": "field",
        "W": "field",
        "C": "monastery"
    },
    "connections": {
        "N": ["E", "S", "W"],
        "E": ["S", "W", "N"],
        "S": ["W", "N", "E"],
        "W": ["N", "E", "S"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_C.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "city",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "N": ["E", "S", "W","C"],
        "E": ["S", "W", "N","C"],
        "S": ["W", "N", "E","C"],
        "W": ["N", "E", "S","C"],
        "C": ["N", "E", "S","W"]
    },
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_D.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "field",
        "W": "road",
        "C": "road"
    },
    "connections": {
        "E": ["W","C"],
        "W": ["E","C"],
        "C": ["E","W"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_E.png",
    "terrains": {
        "N": "city",
        "E": "field",
        "S": "field",
        "W": "field",
        "C": None
    },
    "connections": {
        "E": ["S", "W"],
        "S": ["W", "E"],
        "W": ["E", "S"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_F.png",
    "terrains": {
        "N": "field",
        "E": "city",
        "S": "field",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "E": ["W","C"],
        "W": ["E","C"],
        "C": ["E","W"]
    },
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_G.png",
    "terrains": {
        "N": "field",
        "E": "city",
        "S": "field",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "E": ["W","C"],
        "W": ["E","C"],
        "C": ["E","W"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_H.png",
    "terrains": {
        "N": "city",
        "E": "field",
        "S": "city",
        "W": "field",
        "C": "field"
    },
    "connections": {
        "E": ["W","C"],
        "W": ["E","C"],
        "C": ["E","W"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_I.png",
    "terrains": {
        "N": "city",
        "E": "field",
        "S": "field",
        "W": "city",
        "C": "field"
    },
    "connections": {
        "E": ["S","C"],
        "S": ["E","C"],
        "C": ["E","S"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_J.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "field",
        "C": None
    },
    "connections": {
        "E": ["S"],
        "S": ["E"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_K.png",
    "terrains": {
        "N": "city",
        "E": "field",
        "S": "road",
        "W": "road",
        "C": "road"
    },
    "connections": {
        "S": ["W","C"],
        "W": ["S","C"],
        "C": ["S","W"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_L.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "road",
        "C": None
    },
    "connections": None,
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_M.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "field",
        "W": "field",
        "C": None
    },
    "connections": {
        "N": ["E"],
        "E": ["N"],
        "S": ["W"],
        "W": ["S"]
    },
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_N.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "field",
        "W": "field",
        "C": None
    },
    "connections": {
        "N": ["E"],
        "E": ["N"],
        "S": ["W"],
        "W": ["S"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_O.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "city",
        "C": None
    },
    "connections": {
        "N": ["W"],
        "E": ["S"],
        "S": ["E"],
        "W": ["N"]
    },
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_P.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "city",
        "C": None
    },
    "connections": {
        "N": ["W"],
        "E": ["S"],
        "S": ["E"],
        "W": ["N"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_Q.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "field",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "N": ["E", "W","C"],
        "E": ["W", "N","C"],
        "W": ["N", "E","C"],
        "C": ["N", "E","W"]
    },
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_R.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "field",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "N": ["E", "W","C"],
        "E": ["W", "N","C"],
        "W": ["N", "E","C"],
        "C": ["N", "E","W"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_S.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "road",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "N": ["E", "W","C"],
        "E": ["W", "N","C"],
        "W": ["N", "E","C"],
        "C": ["N", "E","W"]
    },
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_T.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "road",
        "W": "city",
        "C": "city"
    },
    "connections": {
        "N": ["E", "W","C"],
        "E": ["W", "N","C"],
        "W": ["N", "E","C"],
        "C": ["N", "E","W"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_U.png",
    "terrains": {
        "N": "road",
        "E": "field",
        "S": "road",
        "W": "field",
        "C": "road"
    },
    "connections": {
        "N": ["S","C"],
        "S": ["N","C"],
        "C": ["N","S"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_V.png",
    "terrains": {
        "N": "field",
        "E": "field",
        "S": "road",
        "W": "road",
        "C": "field"
    },
    "connections": {
        "N": ["E","C"],
        "E": ["N","C"],
        "S": ["W"],
        "W": ["S"],
        "C": ["N","E"]
    },
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_W.png",
    "terrains": {
        "N": "field",
        "E": "road",
        "S": "road",
        "W": "road",
        "C": None
    },
    "connections": None,
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_X.png",
    "terrains": {
        "N": "road",
        "E": "road",
        "S": "road",
        "W": "road",
        "C": None
    },
    "connections": None,
    "features": None
}]

CARD_DISTRIBUTIONS = {
    "base_game/Base_Game_C3_Tile_A.png": 2,
    "base_game/Base_Game_C3_Tile_B.png": 4,
    "base_game/Base_Game_C3_Tile_C.png": 1,
    "base_game/Base_Game_C3_Tile_D.png": 4,
    "base_game/Base_Game_C3_Tile_E.png": 5,
    "base_game/Base_Game_C3_Tile_F.png": 2,
    "base_game/Base_Game_C3_Tile_G.png": 1,
    "base_game/Base_Game_C3_Tile_H.png": 3,
    "base_game/Base_Game_C3_Tile_I.png": 2,
    "base_game/Base_Game_C3_Tile_J.png": 3,
    "base_game/Base_Game_C3_Tile_K.png": 3,
    "base_game/Base_Game_C3_Tile_L.png": 3,
    "base_game/Base_Game_C3_Tile_M.png": 2,
    "base_game/Base_Game_C3_Tile_N.png": 3,
    "base_game/Base_Game_C3_Tile_O.png": 2,
    "base_game/Base_Game_C3_Tile_P.png": 3,
    "base_game/Base_Game_C3_Tile_Q.png": 1,
    "base_game/Base_Game_C3_Tile_R.png": 3,
    "base_game/Base_Game_C3_Tile_S.png": 2,
    "base_game/Base_Game_C3_Tile_T.png": 1,
    "base_game/Base_Game_C3_Tile_U.png": 8,
    "base_game/Base_Game_C3_Tile_V.png": 9,
    "base_game/Base_Game_C3_Tile_W.png": 4,
    "base_game/Base_Game_C3_Tile_X.png": 1
}


def get_card_definitions():
    """Return the card definitions for the base game."""
    return CARD_DEFINITIONS


def get_card_distributions():
    """Return the card distributions for the base game."""
    return CARD_DISTRIBUTIONS
