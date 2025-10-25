"""Utility functions for data serialization and caching."""

import pickle
from typing import Any


def store_pkl(filename: str, data: Any) -> None:
    """
    Store an object to a pickle file.

    Args:
        filename: Path to the pickle file
        data: Object to serialize and store

    Raises:
        IOError: If file cannot be written
        pickle.PicklingError: If object cannot be pickled
    """
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_pkl(filename: str) -> Any:
    """
    Load an object from a pickle file.

    Args:
        filename: Path to the pickle file

    Returns:
        The deserialized object

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
        pickle.UnpicklingError: If file cannot be unpickled
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)
