import random

class Structure:
    
    def __init__(self, structureType):
        """
        Init structure
        :param structureType: Type of the structure ('City', 'Road', 'Monastery', 'Field')
        """
        
        self.structureType = structureType
        #self.cards = [] # List of cards that are part of the structure
        self.cardSides = set()  # Store (card, direction) tuples here
        self.figures = [] # List of figures placed in this structure
        self.isCompleted = False # Tracking whether the structure has been completed
        self.color = (
            random.randint(0, 255),  # R
            random.randint(0, 255),  # G
            random.randint(0, 255),  # B
            150                      # Alpha for transparency
        )

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
        
    def addCardSide(self, card, direction):
        #self.cards.append(card)
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
            
    def getFigureOwner(self):
        """
        Returns owner of the figure placed in the structure
        :return: The player who owns the figure
        """
        if self.figures:
            return self.figures[0].getOwner()
        return None
        
    def merge(self, otherStructure):
        #self.cards.update(otherStructure.cards)
        self.cardSides.update(otherStructure.cardSides)