"""
Card Set Loader
Dynamically discovers and loads all available card sets.
"""

import os
import importlib
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def discover_card_sets() -> List[str]:
    """
    Discover all available card set modules in the card_sets directory.
    Returns a list of module names (excluding __init__.py and setLoader.py).
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    card_sets = []

    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and not filename.startswith(
                '__') and filename != 'setLoader.py':
            module_name = filename[:-3]  # Remove .py extension
            card_sets.append(module_name)

    logger.debug(f"Discovered card sets: {card_sets}")
    return card_sets


def load_card_set(set_name: str) -> Dict[str, Any]:
    """
    Load a specific card set by name.
    Returns a dictionary with 'definitions' and 'distributions' keys.
    """
    try:
        module = importlib.import_module(f'models.card_sets.{set_name}')

        # Get card definitions
        if hasattr(module, 'get_card_definitions'):
            definitions = module.get_card_definitions()
        elif hasattr(module, 'CARD_DEFINITIONS'):
            definitions = module.CARD_DEFINITIONS
        else:
            logger.warning(f"Card set {set_name} has no card definitions")
            definitions = []

        # Get card distributions
        if hasattr(module, 'get_card_distributions'):
            distributions = module.get_card_distributions()
        elif hasattr(module, 'CARD_DISTRIBUTIONS'):
            distributions = module.CARD_DISTRIBUTIONS
        else:
            logger.warning(f"Card set {set_name} has no card distributions")
            distributions = {}

        return {
            'definitions': definitions,
            'distributions': distributions,
            'name': set_name
        }

    except ImportError as e:
        logger.error(f"Failed to load card set {set_name}: {e}")
        return {'definitions': [], 'distributions': {}, 'name': set_name}
    except Exception as e:
        logger.error(f"Error loading card set {set_name}: {e}")
        return {'definitions': [], 'distributions': {}, 'name': set_name}


def load_all_card_sets() -> Dict[str, Any]:
    """
    Load all available card sets and combine their definitions.
    Returns a combined dictionary with all card definitions and distributions.
    """
    card_sets = discover_card_sets()
    all_definitions = []
    all_distributions = {}

    for set_name in card_sets:
        set_data = load_card_set(set_name)
        if set_data['definitions']:
            all_definitions.extend(set_data['definitions'])
            all_distributions.update(set_data['distributions'])
            logger.info(
                f"Loaded card set: {set_name} with {len(set_data['definitions'])} card definitions"
            )

    logger.info(f"Total card definitions loaded: {len(all_definitions)}")
    logger.info(f"Total card distributions: {len(all_distributions)}")

    return {'definitions': all_definitions, 'distributions': all_distributions}


def get_available_card_sets() -> List[Dict[str, Any]]:
    """
    Get a list of available card sets with their metadata.
    Returns a list of dictionaries with 'name', 'display_name', and 'description' keys.
    """
    card_sets = discover_card_sets()
    available_sets = []

    for set_name in card_sets:
        set_data = load_card_set(set_name)
        if set_data['definitions']:
            display_name = 'Unknown Expansion'
            try:
                module = importlib.import_module(
                    f'models.card_sets.{set_name}')
                if hasattr(module, 'CARD_SET_NAME'):
                    display_name = module.CARD_SET_NAME
            except:
                pass

            description = f"{len(set_data['definitions'])} cards"
            try:
                module = importlib.import_module(
                    f'models.card_sets.{set_name}')
                if hasattr(module, '__doc__') and module.__doc__:
                    description = module.__doc__.strip().split('\n')[0]
            except:
                pass

            available_sets.append({
                'name': set_name,
                'display_name': display_name,
                'description': description,
                'card_count': len(set_data['definitions'])
            })

    return available_sets
