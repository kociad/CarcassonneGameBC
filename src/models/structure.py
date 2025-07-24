import random
import logging
import typing
from models.figure import Figure
import settings

logger = logging.getLogger(__name__)

class Structure:
    """Represents a structure (city, road, monastery, or field) in the game."""
    def __init__(self, structureType: str) -> None:
        """
        Initialize a structure.
        :param structureType: Type of the structure ('City', 'Road', 'Monastery', 'Field').
        """
        self.structureType = structureType
        self.cards = []
        self.cardSides = set()
        self.figures = []
        self.isCompleted = False
        self.color = (255, 255, 255, 150)

    def getStructureType(self) -> str:
        """Return the structure type."""
        return self.structureType

    def getColor(self) -> tuple:
        """Return the structure color."""
        return self.color

    def getIsCompleted(self) -> bool:
        """Return True if the structure is completed."""
        return self.isCompleted

    def getFigures(self) -> list:
        """Return the list of figures assigned to this structure."""
        return self.figures

    def setColor(self, color: tuple) -> None:
        """Set the color of the structure."""
        self.color = color

    def setFigures(self, figures: list) -> None:
        """Set the figures for this structure."""
        self.figures = figures

    def addCardSide(self, card: typing.Any, direction: str) -> None:
        """Add a card and direction to the structure."""
        if not card in self.cards:
            self.cards.append(card)
        self.cardSides.add((card, direction))

    def addFigure(self, figure: typing.Any) -> bool:
        """Add a figure to the structure if not already claimed."""
        if not self.figures:
            self.figures.append(figure)
            return True
        return False

    def removeFigure(self, figure: typing.Any) -> None:
        """Remove a figure from the structure and clear its placement."""
        logger.debug(f"Removing figure {figure} belonging to {figure.getOwner()}")
        self.figures.remove(figure)
        figure.remove()

    def checkCompletion(self) -> None:
        """Check if the structure is completed and update its status."""
        if self.structureType == "City":
            self.isCompleted = self.checkCityCompletion()
        elif self.structureType == "Road":
            self.isCompleted = self.checkRoadCompletion()
        elif self.structureType == "Monastery":
            self.isCompleted = self.checkMonasteryCompletion()
        elif self.structureType == "Field":
            self.isCompleted = self.checkFieldCompletion()

    def checkCityCompletion(self) -> bool:
        """Return True if the city structure is completed."""
        for card, direction in self.cardSides:
            neighborCard = card.getNeighbors().get(direction)
            if not neighborCard:
                return False
        return True

    def checkRoadCompletion(self) -> bool:
        """Return True if the road structure is completed."""
        for card, direction in self.cardSides:
            neighborCard = card.getNeighbors().get(direction)
            if not neighborCard:
                return False
        return True

    def checkMonasteryCompletion(self) -> bool:
        """Return True if the monastery structure is completed."""
        for card, direction in self.cardSides:
            neighbors = card.getNeighbors()
            for direction in neighbors:
                if not neighbors[direction]:
                    return False
                if direction in ["N", "S"] and not (neighbors[direction].getNeighbor("W") and neighbors[direction].getNeighbor("E")):
                    return False
        return True

    def checkFieldCompletion(self) -> bool:
        """Return True if the field structure is completed (always False)."""
        return False

    def getMajorityOwners(self) -> list:
        """Return the player(s) with the most figures in this structure."""
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

    def merge(self, otherStructure: 'Structure') -> None:
        """Merge another structure into this one."""
        self.cardSides.update(otherStructure.cardSides)
        for figure in otherStructure.figures:
            self.figures.append(figure)
        for card in otherStructure.cards:
            self.cards.append(card)

    def getScore(self, gameSession: typing.Any = None) -> int:
        """Calculate and return the score for this structure."""
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
                score += 1
                neighbors = card.getNeighbors()
                for direction in neighbors:
                    if neighbors[direction]:
                        score += 1
                        if direction in ["N", "S"]:
                            if neighbors[direction].getNeighbor("W"):
                                score += 1
                            if neighbors[direction].getNeighbor("E"):
                                score += 1
        elif self.structureType == "Field" and gameSession:
            if settings.DEBUG:
                self.isCompleted = True
            scoredCities = set()
            completedCities = [
                s for s in gameSession.structures
                if s.getStructureType() == "City" and s.getIsCompleted()
            ]
            for card, _ in self.cardSides:
                neighbors = card.getNeighbors().values()
                touchedCards = set([card])
                touchedCards.update([n for n in neighbors if n])
                for cityStructure in completedCities:
                    for cityCard, _ in cityStructure.cardSides:
                        if cityCard in touchedCards:
                            scoredCities.add(cityStructure)
                            break
            score = len(scoredCities) * 3
        return score

    def serialize(self) -> dict:
        """Serialize the structure to a dictionary."""
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
    def deserialize(data: dict, gameBoard: typing.Any, playerMap: dict, placedFigures: list) -> 'Structure':
        """Deserialize a structure from a dictionary."""
        s = Structure(data["structure_type"])
        s.isCompleted = bool(data.get("is_completed", False))
        raw_color = data.get("color", (255, 255, 255, 150))
        try:
            s.color = tuple(int(c) for c in raw_color)
        except Exception as e:
            logger.warning(f"Failed to parse color: {raw_color} - {e}")
            s.color = (255, 255, 255, 150)
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
                matched = next(
                    (fig for fig in placedFigures
                     if fig.owner == owner and fig.card == card and fig.positionOnCard == position),
                    None
                )
                if matched:
                    s.figures.append(matched)
                else:
                    logger.warning(f"No matching figure found in placedFigures for: {f}")
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed figure: {f} - {e}")
        return s
