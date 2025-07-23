import importlib
import logging
from typing import Any, Dict, List, Callable

logger = logging.getLogger(__name__)

class SettingsManager:
    """
    Manages settings loaded from settings.py with runtime modifications
    and change notifications.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.observers: Dict[str, List[Callable]] = {}
        self._runtime_overrides: Dict[str, Any] = {}
        self._original_settings: Dict[str, Any] = {}
        
        self._loadFromSettingsFile()
        
    def _loadFromSettingsFile(self):
        """Load settings from settings.py module"""
        try:
            # Import or reload settings module
            import settings
            importlib.reload(settings)
            
            # Store all settings that don't start with underscore
            for attr_name in dir(settings):
                if not attr_name.startswith('_'):
                    value = getattr(settings, attr_name)
                    # Only store simple types (not functions, classes, etc.)
                    if isinstance(value, (int, float, str, bool, list, dict, tuple)):
                        self._original_settings[attr_name] = value
                        
            logger.debug(f"Loaded {len(self._original_settings)} settings from settings.py")
            
        except Exception as e:
            logger.error(f"Failed to load settings.py: {e}")
            # Fallback defaults
            self._original_settings = {
                "WINDOW_WIDTH": 1920,
                "WINDOW_HEIGHT": 1080,
                "FULLSCREEN": False,
                "TILE_SIZE": 96,
                "FIGURE_SIZE": 25,
                "DEBUG": True,
                "NETWORK_MODE": "local",
                "HOST_IP": "0.0.0.0",
                "HOST_PORT": 222,
                "PLAYERS": ["Player 1", "Player 2"],
                "SIDEBAR_WIDTH": 200,
                "GAME_LOG_MAX_ENTRIES": 2000
            }
    
    def get(self, key: str, fallback: Any = None) -> Any:
        """Get a setting value (runtime override takes precedence)"""
        if key in self._runtime_overrides:
            return self._runtime_overrides[key]
        elif key in self._original_settings:
            return self._original_settings[key]
        else:
            logger.warning(f"Unknown setting requested: {key}")
            return fallback
    
    def set(self, key: str, value: Any, temporary: bool = True) -> bool:
        """
        Set a setting value
        :param key: Setting name
        :param value: New value
        :param temporary: If True, only changes runtime (default). If False, modifies settings.py
        """
        old_value = self.get(key)
        
        if temporary:
            # Store as runtime override
            self._runtime_overrides[key] = value
            logger.debug(f"Runtime setting {key} changed from {old_value} to {value}")
        else:
            # Modify settings.py file directly
            if self._updateSettingsFile(key, value):
                self._original_settings[key] = value
                # Remove from runtime overrides since it's now in the file
                self._runtime_overrides.pop(key, None)
                logger.debug(f"Permanent setting {key} changed from {old_value} to {value}")
            else:
                return False
        
        # Notify observers
        self._notifyObservers(key, old_value, value)
        return True
    
    def _updateSettingsFile(self, key: str, value: Any) -> bool:
        """Update a setting in the settings.py file"""
        try:
            import settings
            settings_path = settings.__file__
            
            with open(settings_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find and update the line
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key} ="):
                    # Format value appropriately
                    if isinstance(value, str):
                        formatted_value = f'"{value}"'
                    elif isinstance(value, list):
                        formatted_value = str(value)
                    else:
                        formatted_value = str(value)
                    
                    lines[i] = f"{key} = {formatted_value}\n"
                    updated = True
                    break
            
            if updated:
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                # Reload the module to reflect changes
                #importlib.reload(settings)
                return True
            else:
                logger.warning(f"Setting {key} not found in settings.py")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update settings.py: {e}")
            return False
    
    def reloadFromFile(self):
        """Reload settings from settings.py (discards runtime overrides)"""
        self._runtime_overrides.clear()
        self._loadFromSettingsFile()
        logger.debug("Settings reloaded from file")
    
    def getTemporaryChanges(self) -> Dict[str, Any]:
        """Get all temporary (runtime) changes"""
        return self._runtime_overrides.copy()
    
    def makePermanent(self, key: str = None) -> bool:
        """Make runtime changes permanent by writing to settings.py"""
        if key:
            if key in self._runtime_overrides:
                return self.set(key, self._runtime_overrides[key], temporary=False)
            return True
        else:
            # Make all runtime changes permanent
            success = True
            for k, v in self._runtime_overrides.copy().items():
                if not self.set(k, v, temporary=False):
                    success = False
            return success
    
    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Subscribe to changes for a specific setting"""
        if key not in self.observers:
            self.observers[key] = []
        self.observers[key].append(callback)
    
    def unsubscribe(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Unsubscribe from changes for a specific setting"""
        if key in self.observers and callback in self.observers[key]:
            self.observers[key].remove(callback)
    
    def _notifyObservers(self, key: str, old_value: Any, new_value: Any):
        """Notify all observers of a setting change"""
        if key in self.observers:
            for callback in self.observers[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    logger.error(f"Observer callback failed for {key}: {e}")

# Global singleton instance
settings_manager = SettingsManager()