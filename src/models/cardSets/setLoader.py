"""
Card Set Loader
Dynamically discovers and loads all available card sets.
"""

import os
import importlib
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def discoverCardSets() -> List[str]:
    """
    Discover all available card set modules in the cardSets directory.
    Returns a list of module names (excluding __init__.py and setLoader.py).
    """
    currentDir = os.path.dirname(os.path.abspath(__file__))
    cardSets = []
    
    for filename in os.listdir(currentDir):
        if filename.endswith('.py') and not filename.startswith('__') and filename != 'setLoader.py':
            moduleName = filename[:-3]  # Remove .py extension
            cardSets.append(moduleName)
    
    logger.debug(f"Discovered card sets: {cardSets}")
    return cardSets

def loadCardSet(setName: str) -> Dict[str, Any]:
    """
    Load a specific card set by name.
    Returns a dictionary with 'definitions' and 'distributions' keys.
    """
    try:
        module = importlib.import_module(f'models.cardSets.{setName}')
        
        # Get card definitions
        if hasattr(module, 'getCardDefinitions'):
            definitions = module.getCardDefinitions()
        elif hasattr(module, 'CARD_DEFINITIONS'):
            definitions = module.CARD_DEFINITIONS
        else:
            logger.warning(f"Card set {setName} has no card definitions")
            definitions = []
        
        # Get card distributions
        if hasattr(module, 'getCardDistributions'):
            distributions = module.getCardDistributions()
        elif hasattr(module, 'CARD_DISTRIBUTIONS'):
            distributions = module.CARD_DISTRIBUTIONS
        else:
            logger.warning(f"Card set {setName} has no card distributions")
            distributions = {}
        
        return {
            'definitions': definitions,
            'distributions': distributions,
            'name': setName
        }
        
    except ImportError as e:
        logger.error(f"Failed to load card set {setName}: {e}")
        return {'definitions': [], 'distributions': {}, 'name': setName}
    except Exception as e:
        logger.error(f"Error loading card set {setName}: {e}")
        return {'definitions': [], 'distributions': {}, 'name': setName}

def loadAllCardSets() -> Dict[str, Any]:
    """
    Load all available card sets and combine their definitions.
    Returns a combined dictionary with all card definitions and distributions.
    """
    cardSets = discoverCardSets()
    allDefinitions = []
    allDistributions = {}
    
    for setName in cardSets:
        setData = loadCardSet(setName)
        if setData['definitions']:
            allDefinitions.extend(setData['definitions'])
            allDistributions.update(setData['distributions'])
            logger.info(f"Loaded card set: {setName} with {len(setData['definitions'])} card definitions")
    
    logger.info(f"Total card definitions loaded: {len(allDefinitions)}")
    logger.info(f"Total card distributions: {len(allDistributions)}")
    
    return {
        'definitions': allDefinitions,
        'distributions': allDistributions
    }

def getAvailableCardSets() -> List[Dict[str, Any]]:
    """
    Get a list of available card sets with their metadata.
    Returns a list of dictionaries with 'name', 'displayName', and 'description' keys.
    """
    cardSets = discoverCardSets()
    availableSets = []
    
    for setName in cardSets:
        setData = loadCardSet(setName)
        if setData['definitions']:
            displayName = 'Unknown Expansion'
            try:
                module = importlib.import_module(f'models.cardSets.{setName}')
                if hasattr(module, 'CARD_SET_NAME'):
                    displayName = module.CARD_SET_NAME
            except:
                pass
            
            description = f"{len(setData['definitions'])} cards"
            try:
                module = importlib.import_module(f'models.cardSets.{setName}')
                if hasattr(module, '__doc__') and module.__doc__:
                    description = module.__doc__.strip().split('\n')[0]
            except:
                pass
            
            availableSets.append({
                'name': setName,
                'displayName': displayName,
                'description': description,
                'cardCount': len(setData['definitions'])
            })
    
    return availableSets 