"""
Base Game Card Set for Carcassonne
Contains all the standard tiles from the base game.
"""

CARD_SET_NAME = "Base Game"

CARD_DEFINITIONS = [{
    "image": "base_game/Base_Game_C3_Tile_A.png",
    "terrains": {
        "N": "field",
        "E": "field",
        "S": "road",
        "W": "field",
        "C": "monastery",
        "SE": "field",
        "SW": "field"

    },
    "connection_groups": [["N","E","W","SE","SW"]],
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
    "connection_groups": [["N","E","S","W"]],
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
    "connection_groups": [["N","E","S","W","C"]],
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_D.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "field",
        "W": "road",
        "C": "road",
        "SW": "field",
        "SE": "field"
    },
    "connection_groups": [["E","W","C"], ["SE","S","SW"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_E.png",
    "terrains": {
        "N": "city",
        "E": "field",
        "S": "field",
        "W": "field",
        "C": "city"
    },
    "connection_groups": [["N","C"],["E","S","W"]],
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
    "connection_groups": [["E","W","C"]],
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
    "connection_groups": [["E","W","C"]],
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
    "connection_groups": [["E","W","C"]],
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
    "connection_groups": [["E","S","C"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_J.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "field",
        "C": "road",
        "SE": "field",
        "SW": "field"
    },
    "connection_groups": [["E","S","C"], ["W","SW"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_K.png",
    "terrains": {
        "N": "city",
        "E": "field",
        "S": "road",
        "W": "road",
        "C": "road",
        "SE": "field",
        "SW": "field"
    },
    "connection_groups": [["S","W","C"], ["E", "SE"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_L.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "road",
        "C": None,
        "SE": "field",
        "SW": "field"
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
        "C": "city"
    },
    "connection_groups": [["N","E","C"],["S","W"]],
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_N.png",
    "terrains": {
        "N": "city",
        "E": "city",
        "S": "field",
        "W": "field",
        "C": "city"
    },
    "connection_groups": [["N","E","C"],["S","W"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_O.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "city",
        "C": "city",
        "SE": "field"
    },
    "connection_groups": [["N","W","C"],["E","S"]],
    "features": ["coat"]
}, {
    "image": "base_game/Base_Game_C3_Tile_P.png",
    "terrains": {
        "N": "city",
        "E": "road",
        "S": "road",
        "W": "city",
        "C": "city",
        "SE": "field"
    },
    "connection_groups": [["N","W","C"],["E","S"]],
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
    "connection_groups": [["N","E","W","C"]],
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
    "connection_groups": [["N","E","W","C"]],
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
    "connection_groups": [["N","E","W","C"]],
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
    "connection_groups": [["N","E","W","C"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_U.png",
    "terrains": {
        "N": "road",
        "E": "field",
        "S": "road",
        "W": "field",
        "C": "road",
        "NE": "field",
        "NW": "field",
        "SE": "field",
        "SW": "field"
    },
    "connection_groups": [["N","S","C"], ["NE","E","SE"], ["NW","W","SW"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_V.png",
    "terrains": {
        "N": "field",
        "E": "field",
        "S": "road",
        "W": "road",
        "C": "road",
        "SW": "field",
        "SE": "field",
        "NE": "field",
        "NW": "field"
    },
    "connection_groups": [["N","E","SE","NW","NE"],["S","W","C"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_W.png",
    "terrains": {
        "N": "field",
        "E": "road",
        "S": "road",
        "W": "road",
        "C": None,
        "SE": "field",
        "SW": "field",
        "NE": "field",
        "NW": "field"
    },
    "connection_groups": [["N","NE","NW"]],
    "features": None
}, {
    "image": "base_game/Base_Game_C3_Tile_X.png",
    "terrains": {
        "N": "road",
        "E": "road",
        "S": "road",
        "W": "road",
        "C": None,
        "NE": "field",
        "NW": "field",
        "SE": "field",
        "SW": "field"
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
