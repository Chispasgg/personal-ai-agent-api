"""
JSON file I/O utilities.
"""
import json
from pathlib import Path
from typing import Any, Dict


def read_json(file_path: str | Path) -> Dict[str, Any]:
    """
    Read JSON from file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Read JSON file, path: {str(file_path)}")
    return data


def write_json(file_path: str | Path, data: Dict[str, Any], indent: int=2) -> None:
    """
    Write JSON to file.

    Args:
        file_path: Path to JSON file
        data: Data to write
        indent: JSON indentation level
    """
    path = Path(file_path)

    # Create parent directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    print(f"Wrote JSON file, path: {str(file_path)}")


def append_to_json_array(file_path: str | Path, item: Dict[str, Any]) -> None:
    """
    Append item to JSON array file.
    Creates file with array if it doesn't exist.

    Args:
        file_path: Path to JSON file
        item: Item to append
    """
    path = Path(file_path)

    # Read existing data or start with empty array
    if path.exists():
        try:
            data = read_json(path)
            if not isinstance(data, list):
                print("File is not a JSON array, will be overwritten")
                data = []
        except json.JSONDecodeError:
            print("Invalid JSON file, will be overwritten")
            data = []
    else:
        data = []

    # Append and write
    data.append(item)
    write_json(path, data)


def safe_read_json(file_path: str | Path, default: Any = ...) -> Any:
    """
    Safely read JSON file with default fallback.

    Args:
        file_path: Path to JSON file
        default: Default value if read fails (defaults to {})

    Returns:
        JSON data or default value
    """
    try:
        return read_json(file_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to read JSON file, path: {str(file_path)}, error: {str(e)}")
        return {} if default is ... else default
