"""
Configuration Manager for Waybridge Agent
Handles loading, validation, and management of configuration settings
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass


class ConfigManager:
    """Manages application configuration with validation and defaults"""
    
    DEFAULT_CONFIG = {
        "serial": {
            "port": "COM3",
            "baudrate": 9600,
            "timeout": 1,
            "bytesize": 8,
            "parity": "N",
            "stopbits": 1
        },
        "erp": {
            "url": "",
            "token": "",
            "timeout": 10,
            "retry_attempts": 3,
            "retry_delay": 2
        },
        "weighbridge": {
            "id": "WB-01",
            "unit": "kg",
            "precision": 2
        },
        "logging": {
            "level": "INFO",
            "file": "waybridge_agent.log",
            "max_size_mb": 10,
            "backup_count": 5
        },
        "app": {
            "version": "1.0.0",
            "auto_start": False,
            "minimize_to_tray": False
        }
    }
    
    REQUIRED_FIELDS = {
        "serial.port": str,
        "serial.baudrate": int,
        "weighbridge.id": str
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = self._merge_configs(self.DEFAULT_CONFIG.copy(), loaded_config)
                    self._validate_config()
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in config file: {e}")
            except Exception as e:
                raise ConfigurationError(f"Error loading config: {e}")
        else:
            # Create default config file
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Recursively merge two configuration dictionaries
        
        Args:
            base: Base configuration
            override: Configuration to override base
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _validate_config(self) -> None:
        """Validate configuration against required fields and types"""
        for field_path, expected_type in self.REQUIRED_FIELDS.items():
            value = self._get_nested_value(field_path)
            
            if value is None or value == "":
                raise ConfigurationError(f"Required field '{field_path}' is missing or empty")
            
            if not isinstance(value, expected_type):
                raise ConfigurationError(
                    f"Field '{field_path}' must be of type {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
        
        # Additional validations
        self._validate_serial_config()
        self._validate_erp_config()
        self._validate_weighbridge_config()
    
    def _validate_serial_config(self) -> None:
        """Validate serial port configuration"""
        baudrate = self.config["serial"]["baudrate"]
        valid_baudrates = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]
        
        if baudrate not in valid_baudrates:
            raise ConfigurationError(
                f"Invalid baudrate {baudrate}. Must be one of: {valid_baudrates}"
            )
        
        timeout = self.config["serial"]["timeout"]
        if timeout <= 0:
            raise ConfigurationError("Serial timeout must be greater than 0")
    
    def _validate_erp_config(self) -> None:
        """Validate ERP configuration"""
        url = self.config["erp"]["url"]
        
        # Allow empty URL for initial setup, but validate format if provided
        if url and not url.startswith(("http://", "https://")):
            raise ConfigurationError("ERP URL must start with http:// or https://")
        
        timeout = self.config["erp"]["timeout"]
        if timeout <= 0:
            raise ConfigurationError("ERP timeout must be greater than 0")
        
        retry_attempts = self.config["erp"]["retry_attempts"]
        if retry_attempts < 0:
            raise ConfigurationError("Retry attempts cannot be negative")
    
    def _validate_weighbridge_config(self) -> None:
        """Validate weighbridge configuration"""
        wb_id = self.config["weighbridge"]["id"]
        if not wb_id or len(wb_id.strip()) == 0:
            raise ConfigurationError("Weighbridge ID cannot be empty")
        
        precision = self.config["weighbridge"]["precision"]
        if precision < 0 or precision > 10:
            raise ConfigurationError("Precision must be between 0 and 10")
    
    def _get_nested_value(self, path: str) -> Any:
        """
        Get value from nested dictionary using dot notation
        
        Args:
            path: Dot-separated path (e.g., 'serial.port')
            
        Returns:
            Value at the path or None if not found
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """
        Set value in nested dictionary using dot notation
        
        Args:
            path: Dot-separated path (e.g., 'serial.port')
            value: Value to set
        """
        keys = path.split('.')
        target = self.config
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            path: Dot-separated path (e.g., 'serial.port')
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        value = self._get_nested_value(path)
        return value if value is not None else default
    
    def set(self, path: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            path: Dot-separated path (e.g., 'serial.port')
            value: Value to set
        """
        self._set_nested_value(path, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section
        
        Args:
            section: Section name (e.g., 'serial', 'erp')
            
        Returns:
            Configuration section dictionary
        """
        return self.config.get(section, {}).copy()
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        Update entire configuration section
        
        Args:
            section: Section name
            values: Dictionary of values to update
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(values)
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            # Validate before saving
            self._validate_config()
            
            # Create backup of existing config
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.bak')
                self.config_path.rename(backup_path)
            
            # Save new config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Remove backup if save successful
            backup_path = self.config_path.with_suffix('.json.bak')
            if backup_path.exists():
                backup_path.unlink()
                
        except Exception as e:
            # Restore backup if save failed
            backup_path = self.config_path.with_suffix('.json.bak')
            if backup_path.exists():
                backup_path.rename(self.config_path)
            raise ConfigurationError(f"Error saving config: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    def export_config(self, export_path: str) -> None:
        """
        Export configuration to a different file
        
        Args:
            export_path: Path to export file
        """
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def import_config(self, import_path: str) -> None:
        """
        Import configuration from a file
        
        Args:
            import_path: Path to import file
        """
        with open(import_path, 'r', encoding='utf-8') as f:
            imported_config = json.load(f)
        
        self.config = self._merge_configs(self.DEFAULT_CONFIG.copy(), imported_config)
        self._validate_config()
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def __repr__(self) -> str:
        """String representation of config manager"""
        return f"ConfigManager(config_path='{self.config_path}')"


# Singleton instance
_config_instance: Optional[ConfigManager] = None


def get_config(config_path: str = "config.json") -> ConfigManager:
    """
    Get singleton configuration manager instance
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    
    return _config_instance


def reload_config() -> ConfigManager:
    """
    Force reload configuration from file
    
    Returns:
        Reloaded ConfigManager instance
    """
    global _config_instance
    _config_instance = None
    return get_config()


if __name__ == "__main__":
    # Test configuration manager
    try:
        config = get_config()
        print("Configuration loaded successfully!")
        print(f"Serial Port: {config.get('serial.port')}")
        print(f"ERP URL: {config.get('erp.url')}")
        print(f"Weighbridge ID: {config.get('weighbridge.id')}")
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
