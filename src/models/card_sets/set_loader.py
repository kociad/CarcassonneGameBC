"""
Card Set Loader
Dynamically discovers and loads all available card sets.
"""

import os
import importlib
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

ALLOWED_DIRECTIONS = {"N", "E", "S", "W", "C", "NW", "NE", "SW", "SE"}
ALLOWED_TERRAINS = {"city", "road", "monastery", "field"}


def _sanitize_card_definitions(definitions: List[Dict[str, Any]],
                               set_name: str) -> List[Dict[str, Any]]:
    """
    Remove unsupported direction keys from terrains and connections, logging at debug level.
    This prevents odd, non-interactable structures from entering the game.
    """
    sanitized: List[Dict[str, Any]] = []
    for idx, raw_def in enumerate(definitions or []):
        try:
            card_def = dict(raw_def)
            terrains = dict(card_def.get("terrains", {}))
            connections = card_def.get("connections")
            connection_groups = card_def.get("connection_groups")

            unsupported_terrain_keys = [
                d for d in terrains.keys() if d not in ALLOWED_DIRECTIONS
            ]
            if unsupported_terrain_keys:
                logger.debug(
                    f"Card set '{set_name}' card #{idx} ({card_def.get('image','?')}) "
                    f"contains unsupported terrain keys {unsupported_terrain_keys}; ignoring.")
            filtered_terrains = {k: v for k, v in terrains.items() if k in ALLOWED_DIRECTIONS}
            sanitized_terrains = {}
            for dir_key, terrain_value in filtered_terrains.items():
                if terrain_value is None:
                    sanitized_terrains[dir_key] = None
                    continue
                try:
                    terrain_str = str(terrain_value).lower()
                except Exception:
                    terrain_str = None
                if terrain_str not in ALLOWED_TERRAINS:
                    logger.debug(
                        f"Card set '{set_name}' card #{idx} ({card_def.get('image','?')}) "
                        f"has unsupported terrain type '{terrain_value}' at '{dir_key}'; setting to None.")
                    sanitized_terrains[dir_key] = None
                else:
                    sanitized_terrains[dir_key] = terrain_str
            terrains = sanitized_terrains
            card_def["terrains"] = terrains

            base_connections: Dict[str, List[str]] = {}
            
            if isinstance(connection_groups, list):
                for gi, group in enumerate(connection_groups):
                    if not isinstance(group, list):
                        logger.debug(
                            f"Card set '{set_name}' card #{idx} group #{gi} is not a list; skipping.")
                        continue
                    valid = [d for d in group if d in ALLOWED_DIRECTIONS]
                    dropped = set(group) - set(valid)
                    if dropped:
                        logger.debug(
                            f"Card set '{set_name}' card #{idx} ({card_def.get('image','?')}) "
                            f"drops unsupported directions in connection_groups: {sorted(dropped)}.")
                    for from_dir in valid:
                        others = [d for d in valid if d != from_dir]
                        if not others:
                            continue
                        existing = set(base_connections.get(from_dir, []))
                        existing.update(others)
                        base_connections[from_dir] = sorted(existing)

            # Merge/validate explicit connections dict
            if connections is not None:
                if not isinstance(connections, dict):
                    logger.debug(
                        f"Card set '{set_name}' card #{idx} has invalid connections type; dropping.")
                    connections = None
                else:
                    for from_dir, to_list in connections.items():
                        if from_dir not in ALLOWED_DIRECTIONS:
                            logger.debug(
                                f"Card set '{set_name}' card #{idx} ({card_def.get('image','?')}) "
                                f"connection from unsupported '{from_dir}'; ignoring.")
                            continue
                        if not isinstance(to_list, list):
                            continue
                        filtered_to = [d for d in to_list if d in ALLOWED_DIRECTIONS]
                        dropped = set(to_list) - set(filtered_to)
                        if dropped:
                            logger.debug(
                                f"Card set '{set_name}' card #{idx} ({card_def.get('image','?')}) "
                                f"drops unsupported connection targets {sorted(dropped)} from '{from_dir}'.")
                        if filtered_to:
                            merged = set(base_connections.get(from_dir, []))
                            merged.update(filtered_to)
                            base_connections[from_dir] = sorted(merged)

            card_def["connections"] = base_connections if base_connections else None
            # Remove helper field if present, to avoid leaking into runtime
            if "connection_groups" in card_def:
                del card_def["connection_groups"]

            sanitized.append(card_def)
        except Exception as e:
            logger.debug(
                f"Failed to sanitize card definition #{idx} in set '{set_name}': {e}")
            sanitized.append(raw_def)
    return sanitized


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

        definitions = _sanitize_card_definitions(definitions, set_name)

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
