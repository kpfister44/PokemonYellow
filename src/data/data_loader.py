# ABOUTME: Data loading utilities for JSON and YAML files
# ABOUTME: Provides caching and validation for game data files

import json
import yaml
import os


class DataLoader:
    """Handles loading and caching of game data from JSON/YAML files."""

    def __init__(self):
        """Initialize the data loader with an empty cache."""
        self.cache = {}

    def load_json(self, filepath, use_cache=True):
        """
        Load a JSON file with optional caching.

        Args:
            filepath: Path to the JSON file
            use_cache: Whether to cache the loaded data

        Returns:
            Parsed JSON data as a dict

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        # Check cache first
        if use_cache and filepath in self.cache:
            return self.cache[filepath]

        # Load from file
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Cache if requested
        if use_cache:
            self.cache[filepath] = data

        return data

    def load_yaml(self, filepath, use_cache=True):
        """
        Load a YAML file with optional caching.

        Args:
            filepath: Path to the YAML file
            use_cache: Whether to cache the loaded data

        Returns:
            Parsed YAML data

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        # Check cache first
        if use_cache and filepath in self.cache:
            return self.cache[filepath]

        # Load from file
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        # Cache if requested
        if use_cache:
            self.cache[filepath] = data

        return data

    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()

    def remove_from_cache(self, filepath):
        """Remove a specific file from the cache."""
        if filepath in self.cache:
            del self.cache[filepath]


# Global data loader instance
_data_loader = DataLoader()


def load_json(filepath, use_cache=True):
    """Global function to load JSON using the shared data loader."""
    return _data_loader.load_json(filepath, use_cache)


def load_yaml(filepath, use_cache=True):
    """Global function to load YAML using the shared data loader."""
    return _data_loader.load_yaml(filepath, use_cache)


def clear_cache():
    """Global function to clear the data cache."""
    _data_loader.clear_cache()
