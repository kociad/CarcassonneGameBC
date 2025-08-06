import random
import logging
import typing
from models.figure import Figure
import settings

logger = logging.getLogger(__name__)


class Structure:
    """Represents a structure (city, road, monastery, or field) in the game."""

    def __init__(self, structure_type: str) -> None:
        """
        Initialize a structure.
        
        Args:
            structure_type: Type of the structure ('City', 'Road', 'Monastery', 'Field')
        """
        self.structure_type = structure_type
        self.cards = []
        self.card_sides = set()
        self.figures = []
        self.is_completed = False
        self.color = (255, 255, 255, 150)

    def get_structure_type(self) -> str:
        """Get the structure type."""
        return self.structure_type

    def get_color(self) -> tuple:
        """Get the structure color."""
        return self.color

    def get_is_completed(self) -> bool:
        """Check if the structure is completed."""
        return self.is_completed

    def get_figures(self) -> list:
        """Get the list of figures assigned to this structure."""
        return self.figures

    def set_color(self, color: tuple) -> None:
        """
        Set the color of the structure.
        
        Args:
            color: Color to set
        """
        self.color = color

    def set_figures(self, figures: list) -> None:
        """
        Set the figures for this structure.
        
        Args:
            figures: List of figures to set
        """
        self.figures = figures

    def add_card_side(self, card: typing.Any, direction: str) -> None:
        """
        Add a card and direction to the structure.
        
        Args:
            card: Card to add
            direction: Direction on the card
        """
        if not card in self.cards:
            self.cards.append(card)
        self.card_sides.add((card, direction))

    def add_figure(self, figure: typing.Any) -> bool:
        """
        Add a figure to the structure if not already claimed.
        
        Args:
            figure: Figure to add
            
        Returns:
            True if figure was added, False otherwise
        """
        if not self.figures:
            self.figures.append(figure)
            return True
        return False

    def remove_figure(self, figure: typing.Any) -> None:
        """
        Remove a figure from the structure and clear its placement.
        
        Args:
            figure: Figure to remove
        """
        logger.debug(
            f"Removing figure {figure} belonging to {figure.get_owner()}")
        self.figures.remove(figure)
        figure.remove()

    def check_completion(self) -> None:
        """Check if the structure is completed and update its status."""
        if self.structure_type == "City":
            self.is_completed = self._check_city_completion()
        elif self.structure_type == "Road":
            self.is_completed = self._check_road_completion()
        elif self.structure_type == "Monastery":
            self.is_completed = self._check_monastery_completion()
        elif self.structure_type == "Field":
            self.is_completed = self._check_field_completion()

    def _check_city_completion(self) -> bool:
        """Check if the city structure is completed."""
        for card, direction in self.card_sides:
            neighbor_card = card.get_neighbors().get(direction)
            if not neighbor_card:
                return False
        return True

    def _check_road_completion(self) -> bool:
        """Check if the road structure is completed."""
        for card, direction in self.card_sides:
            neighbor_card = card.get_neighbors().get(direction)
            if not neighbor_card:
                return False
        return True

    def _check_monastery_completion(self) -> bool:
        """Check if the monastery structure is completed."""
        for card, direction in self.card_sides:
            neighbors = card.get_neighbors()
            for direction in neighbors:
                if not neighbors[direction]:
                    return False
                if direction in [
                        "N", "S"
                ] and not (neighbors[direction].get_neighbor("W")
                           and neighbors[direction].get_neighbor("E")):
                    return False
        return True

    def _check_field_completion(self) -> bool:
        """Check if the field structure is completed (always False)."""
        return False

    def get_majority_owners(self) -> list:
        """Get the player(s) with the most figures in this structure."""
        logger.debug("Retrieving structure owners...")
        owner_counts = {}
        for figure in self.figures:
            owner = figure.get_owner()
            logger.debug(f"Found figure with owner - {owner}")
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
        if not owner_counts:
            return []
        max_count = max(owner_counts.values())
        logger.debug(f"Retrieved owners: {owner_counts}")
        return [
            owner for owner, count in owner_counts.items()
            if count == max_count
        ]

    def merge(self, other_structure: 'Structure') -> None:
        """
        Merge another structure into this one.
        
        Args:
            other_structure: Structure to merge into this one
        """
        self.card_sides.update(other_structure.card_sides)
        for figure in other_structure.figures:
            self.figures.append(figure)
        for card in other_structure.cards:
            self.cards.append(card)

    def get_score(self, game_session: typing.Any = None) -> int:
        """
        Calculate and return the score for this structure.
        
        Args:
            game_session: Game session for scoring context
            
        Returns:
            Score for this structure
        """
        score = 0
        game_over = game_session.get_game_over()
        if self.structure_type == "City":
            if not game_over:
                for card in self.cards:
                    if card.get_features():
                        score += 2 if "coat" in card.get_features() else 0
                score += len(self.cards) * 2
            else:
                for card in self.cards:
                    if card.get_features():
                        score += 1 if "coat" in card.get_features() else 0
                score += len(self.cards)
        elif self.structure_type == "Road":
            score = len(self.cards)
        elif self.structure_type == "Monastery":
            for card, direction in self.card_sides:
                score += 1
                neighbors = card.get_neighbors()
                for direction in neighbors:
                    if neighbors[direction]:
                        score += 1
                        if direction in ["N", "S"]:
                            if neighbors[direction].get_neighbor("W"):
                                score += 1
                            if neighbors[direction].get_neighbor("E"):
                                score += 1
        elif self.structure_type == "Field" and game_session:
            if settings.DEBUG:
                self.is_completed = True
            scored_cities = set()
            completed_cities = [
                s for s in game_session.structures
                if s.get_structure_type() == "City" and s.get_is_completed()
            ]
            for card, _ in self.card_sides:
                neighbors = card.get_neighbors().values()
                touched_cards = set([card])
                touched_cards.update([n for n in neighbors if n])
                for city_structure in completed_cities:
                    for city_card, _ in city_structure.card_sides:
                        if city_card in touched_cards:
                            scored_cities.add(city_structure)
                            break
            score = len(scored_cities) * 3
        return score

    def serialize(self) -> dict:
        """Serialize the structure to a dictionary."""
        return {
            "structure_type":
            self.structure_type,
            "card_sides": [{
                "x": card_position["X"],
                "y": card_position["Y"],
                "direction": direction
            } for (card, direction) in self.card_sides
                           if (card_position := card.get_position())],
            "figures": [{
                "owner_index":
                f.get_owner().get_index(),
                "position_on_card":
                f.position_on_card,
                "card_position":
                f.card.get_position() if f.card else None
            } for f in self.figures],
            "is_completed":
            self.is_completed,
            "color":
            tuple(self.color) if hasattr(self.color, "__iter__") else
            (255, 255, 255, 150)
        }

    @staticmethod
    def deserialize(data: dict, game_board: typing.Any, player_map: dict,
                    placed_figures: list) -> 'Structure':
        """
        Create a Structure instance from serialized data.
        
        Args:
            data: Serialized structure data
            game_board: The game board
            player_map: Mapping of player indices to player objects
            placed_figures: List of placed figures
            
        Returns:
            Structure instance with restored state
        """
        s = Structure(data["structure_type"])
        s.is_completed = bool(data.get("is_completed", False))
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
                card = game_board.get_card(x, y)
                if card:
                    s.card_sides.add((card, direction))
                    if card not in s.cards:
                        s.cards.append(card)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed cardSide: {side} - {e}")
        for f in data.get("figures", []):
            try:
                owner_index = int(f["owner_index"])
                position = str(f["position_on_card"])
                pos_data = f.get("card_position")
                card = None
                if pos_data and isinstance(pos_data, dict):
                    x = int(pos_data["X"])
                    y = int(pos_data["Y"])
                    card = game_board.get_card(x, y)
                owner = player_map.get(owner_index)
                if not owner:
                    raise ValueError(
                        f"Owner with index {owner_index} not found")
                matched = next((fig for fig in placed_figures
                                if fig.owner == owner and fig.card == card
                                and fig.position_on_card == position), None)
                if matched:
                    s.figures.append(matched)
                else:
                    logger.warning(
                        f"No matching figure found in placed_figures for: {f}")
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed figure: {f} - {e}")
        return s
