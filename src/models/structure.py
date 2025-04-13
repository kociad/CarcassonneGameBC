import random

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
        print(f"Removing figure {figure} belonging to {figure.getOwner()}")
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
        print("Retrieving structure owners...")
        owner_counts = {}
        for figure in self.figures:
            owner = figure.getOwner()
            print(f"Found figure with owner - {owner}")
            owner_counts[owner] = owner_counts.get(owner, 0) + 1

        if not owner_counts:
            return []

        max_count = max(owner_counts.values())
        print(f"Retrieved owners: {owner_counts}")
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
        
    def getScore(self):
        """
        Calculates the score value of this structure.
        Currently supports only cities.
        """
        score = 0
        
        if self.structureType == "City":
            for card in self.cards:
                if card.getFeatures():
                    score = score + 2 if "coat" in card.getFeatures() else score
            score = score + len(self.cards) * 2
            
        elif self.structureType == "Road":
            score = len(self.cards)
            
        elif self.structureType == "Monastery":
            score = 9 if self.isCompleted else 0

        elif self.structureType == "Field":
            score = 0  # TBD
            
        return score