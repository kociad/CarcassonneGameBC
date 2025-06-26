import random
import logging

from models.figure import Figure

from settings import DEBUG

logger = logging.getLogger(__name__)

class Structure:
    
    def __init__(self, structureType):
        """
        Init structure
        :param structureType: Type of the structure ('City', 'Road', 'Monastery', 'Field')
        """
        
        self.structureType = structureType
        self.cards = [] # List of cards that are part of the structure
        self.cardSides = set()  # Store (card, direction) tuples here
        self.figures = [] # List of figures placed in this structure
        self.isCompleted = False # Tracking whether the structure has been completed
        self.color = (255,255,255,150)

    def getStructureType(self):
        """
        Structure type getter method
        :return: Structure type
        """
        return self.structureType
        
    def getColor(self):
        """
        Structure color getter method
        :return: Structure color
        """
        return self.color
        
    def getIsCompleted(self):
        """
        Is completed getter method
        :return: Bool indicating if the structure is completed
        """
        return self.isCompleted
        
    def getFigures(self):
        """
        Structure figure list getter method
        :return: List of figures assigned to given structure
        """
        return self.figures
        
    def setColor(self, color):
        """
        Structure color setter method
        :param color: Color to be set
        """
        self.color = color
        
    def addCardSide(self, card, direction):
        if not card in self.cards:
            self.cards.append(card)
        self.cardSides.add((card, direction))
        
    def addFigure(self, figure):
        """
        Add a figure to the structure
        :param figure: The figure being placed
        """
        if not self.figures:
            self.figures.append(figure)
            return True
        return False # Figure placement denied if structure has already been claimed
        
    def removeFigure(self, figure):
        """
        Remove figure from the structure and clears its placement on card
        :param figure: Figure to be removed
        """
        logger.debug(f"Removing figure {figure} belonging to {figure.getOwner()}")
        self.figures.remove(figure)
        figure.remove()
        
    def checkCompletion(self):
        """
        Check if the structure is completed and set it accordingly
        """
        if self.structureType == "City":
            self.isCompleted = self.checkCityCompletion()
        elif self.structureType == "Road":
            self.isCompleted = self.checkRoadCompletion()
        elif self.structureType == "Monastery":
            self.isCompleted = self.checkMonasteryCompletion()
        elif self.structureType == "Field":
            self.isCompleted = self.checkFieldCompletion()

    def checkCityCompletion(self):
        """
        Check if city structure is completed.
        :return: True if completed, False otherwise
        """
        for card, direction in self.cardSides:
            # Check external neighbor
            neighborCard = card.getNeighbors().get(direction)

            if not neighborCard:
                return False  # Open edge

        return True
        
    def checkRoadCompletion(self):
        """
        Check if road structure is completed.
        :return: True if completed, False otherwise
        """
        for card, direction in self.cardSides:
            # Check external neighbor
            neighborCard = card.getNeighbors().get(direction)

            if not neighborCard:
                return False  # Open edge
                
        return True
        
    def checkMonasteryCompletion(self):
        """
        Check if monastery structure is completed.
        :return: True if completed, False otherwise
        """
        for card, direction in self.cardSides:
            neighbors = card.getNeighbors()
            for direction in neighbors:
                if not neighbors[direction]:
                    return False  # No neighbor in NESW direction
                if direction in ["N","S"] and not (neighbors[direction].getNeighbor("W") and neighbors[direction].getNeighbor("E")):
                    return False  # No diagonal neighbor
                    
        return True
        
    def checkFieldCompletion(self):
        return False
        
    def getMajorityOwners(self):
        """
        Determines player(s) with the most figures in this structure.
        :return: List of Player instances who hold majority.
        """
        logger.debug("Retrieving structure owners...")
        owner_counts = {}
        for figure in self.figures:
            owner = figure.getOwner()
            logger.debug(f"Found figure with owner - {owner}")
            owner_counts[owner] = owner_counts.get(owner, 0) + 1

        if not owner_counts:
            return []

        max_count = max(owner_counts.values())
        logger.debug(f"Retrieved owners: {owner_counts}")
        return [owner for owner, count in owner_counts.items() if count == max_count]
        
    def merge(self, otherStructure):
        """
        Merges another structure into this one by combining cards, card sides, and figures.
        :param otherStructure: The Structure to merge into this one.
        """
        self.cardSides.update(otherStructure.cardSides)
        
        # Merge figures
        for figure in otherStructure.figures:
            self.figures.append(figure)
            
        # Merge cards
        for card in otherStructure.cards:
            self.cards.append(card)
        
    def getScore(self, gameSession=None):
        score = 0
        gameOver = gameSession.getGameOver()

        if self.structureType == "City":
            if not gameOver:
                for card in self.cards:
                    if card.getFeatures():
                        score += 2 if "coat" in card.getFeatures() else 0
                score += len(self.cards) * 2
            else:
                for card in self.cards:
                    if card.getFeatures():
                        score += 1 if "coat" in card.getFeatures() else 0
                score += len(self.cards)

        elif self.structureType == "Road":
            score = len(self.cards)

        elif self.structureType == "Monastery":
            for card, direction in self.cardSides:
                score += 1 # Adding 1 score for the monastery itself
                neighbors = card.getNeighbors()
                for direction in neighbors:
                    if neighbors[direction]:
                        score += 1 # Adding 1 score for each NESW neighbors
                        if direction in ["N","S"]: # Scoring diagonal neighbors
                            if neighbors[direction].getNeighbor("W"):
                                score += 1
                            if neighbors[direction].getNeighbor("E"):
                                score += 1

        elif self.structureType == "Field" and gameSession:
            if DEBUG:
                self.isCompleted = True
            
            scoredCities = set()

            # Get all completed cities
            completedCities = [
                s for s in gameSession.structures
                if s.getStructureType() == "City" and s.getIsCompleted()
            ]

            for card, _ in self.cardSides:
                neighbors = card.getNeighbors().values()
                touchedCards = set([card])  # Include the field's own card
                touchedCards.update([n for n in neighbors if n])  # Add valid neighbor cards

                # Check if any of these cards are part of completed cities
                for cityStructure in completedCities:
                    for cityCard, _ in cityStructure.cardSides:
                        if cityCard in touchedCards:
                            scoredCities.add(cityStructure)
                            break  # No need to scan the rest of this city

            score = len(scoredCities) * 3
            
        return score
        
    def serialize(self):
        return {
            "structure_type": self.structureType,
            "card_sides": [
                {"x": cardPosition["X"], "y": cardPosition["Y"], "direction": direction}
                for (card, direction) in self.cardSides
                if (cardPosition := card.getPosition())
            ],
            "figures": [
                {
                    "owner_index": f.getOwner().getIndex(),
                    "position_on_card": f.positionOnCard,
                    "card_position": f.card.getPosition() if f.card else None
                } for f in self.figures
            ],
            "is_completed": self.isCompleted,
            "color": tuple(self.color) if hasattr(self.color, "__iter__") else (255, 255, 255, 150)
        }
        
    @staticmethod
    def deserialize(data, gameBoard, playerMap):
        s = Structure(data["structure_type"])
        s.isCompleted = bool(data.get("is_completed", False))

        # Ensure color is a tuple of ints
        raw_color = data.get("color", (255, 255, 255, 150))
        try:
            s.color = tuple(int(c) for c in raw_color)
        except Exception as e:
            logger.warning(f"Failed to parse color: {raw_color} - {e}")
            s.color = (255, 255, 255, 150)

        # Rebuild cardSides
        for side in data.get("card_sides", []):
            try:
                x = int(side["x"])
                y = int(side["y"])
                direction = str(side["direction"])
                card = gameBoard.getCard(x, y)
                if card:
                    s.cardSides.add((card, direction))
                    if card not in s.cards:
                        s.cards.append(card)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed card_side: {side} - {e}")

        # Rebuild figures
        for f in data.get("figures", []):
            try:
                owner_index = int(f["owner_index"])
                position = str(f["position_on_card"])
                pos_data = f.get("card_position")
                card = None
                if pos_data and isinstance(pos_data, dict):
                    x = int(pos_data["X"])
                    y = int(pos_data["Y"])
                    card = gameBoard.getCard(x, y)

                owner = playerMap.get(owner_index)
                if not owner:
                    raise ValueError(f"Owner with index {owner_index} not found")

                figure = Figure(owner)
                figure.card = card
                figure.positionOnCard = f["position_on_card"]
                s.addFigure(figure)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed figure: {f} - {e}")

        return s

