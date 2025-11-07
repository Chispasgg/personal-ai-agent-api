"""
Unit tests for jsonio.py module.
"""
import pytest
import json
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.jsonio import read_json, write_json, append_to_json_array, safe_read_json


class TestReadJson:
    """Tests for read_json function."""
    
    def test_read_valid_json(self, tmp_path):
        """Test reading valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        
        # Write test data
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Read and verify
        result = read_json(test_file)
        assert result == test_data
    
    def test_read_nonexistent_file(self, tmp_path):
        """Test reading nonexistent file raises FileNotFoundError."""
        test_file = tmp_path / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            read_json(test_file)
    
    def test_read_invalid_json(self, tmp_path):
        """Test reading invalid JSON raises JSONDecodeError."""
        test_file = tmp_path / "invalid.json"
        
        # Write invalid JSON
        with open(test_file, 'w') as f:
            f.write("not valid json {")
        
        with pytest.raises(json.JSONDecodeError):
            read_json(test_file)
    
    def test_read_json_with_string_path(self, tmp_path):
        """Test reading JSON with string path instead of Path object."""
        test_file = tmp_path / "test.json"
        test_data = {"test": "data"}
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = read_json(str(test_file))
        assert result == test_data


class TestWriteJson:
    """Tests for write_json function."""
    
    def test_write_json_basic(self, tmp_path):
        """Test writing basic JSON data."""
        test_file = tmp_path / "output.json"
        test_data = {"key": "value", "list": [1, 2, 3]}
        
        write_json(test_file, test_data)
        
        # Verify file exists and content is correct
        assert test_file.exists()
        with open(test_file, 'r') as f:
            loaded = json.load(f)
        assert loaded == test_data
    
    def test_write_json_creates_directory(self, tmp_path):
        """Test that write_json creates parent directories."""
        test_file = tmp_path / "nested" / "dir" / "file.json"
        test_data = {"nested": True}
        
        write_json(test_file, test_data)
        
        assert test_file.exists()
        with open(test_file, 'r') as f:
            loaded = json.load(f)
        assert loaded == test_data
    
    def test_write_json_with_indent(self, tmp_path):
        """Test writing JSON with custom indentation."""
        test_file = tmp_path / "indented.json"
        test_data = {"key": "value"}
        
        write_json(test_file, test_data, indent=4)
        
        # Check that file is properly formatted
        with open(test_file, 'r') as f:
            content = f.read()
        assert "    " in content  # 4-space indent
    
    def test_write_json_unicode(self, tmp_path):
        """Test writing JSON with unicode characters."""
        test_file = tmp_path / "unicode.json"
        test_data = {"message": "Hola, ¿cómo estás?", "emoji": "😊"}
        
        write_json(test_file, test_data)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded == test_data
    
    def test_write_json_overwrites_existing(self, tmp_path):
        """Test that write_json overwrites existing file."""
        test_file = tmp_path / "overwrite.json"
        
        # Write initial data
        write_json(test_file, {"old": "data"})
        
        # Overwrite
        new_data = {"new": "data"}
        write_json(test_file, new_data)
        
        with open(test_file, 'r') as f:
            loaded = json.load(f)
        assert loaded == new_data


class TestAppendToJsonArray:
    """Tests for append_to_json_array function."""
    
    def test_append_to_new_file(self, tmp_path):
        """Test appending to nonexistent file creates array."""
        test_file = tmp_path / "array.json"
        item = {"id": 1, "name": "First"}
        
        append_to_json_array(test_file, item)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0] == item
    
    def test_append_to_existing_array(self, tmp_path):
        """Test appending to existing array."""
        test_file = tmp_path / "array.json"
        initial_data = [{"id": 1}, {"id": 2}]
        
        # Create initial file
        write_json(test_file, initial_data)
        
        # Append new item
        new_item = {"id": 3}
        append_to_json_array(test_file, new_item)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 3
        assert data[2] == new_item
    
    def test_append_to_non_array_overwrites(self, tmp_path):
        """Test appending to non-array file overwrites it."""
        test_file = tmp_path / "not_array.json"
        
        # Create file with dict instead of array
        write_json(test_file, {"not": "array"})
        
        # Append should overwrite
        item = {"id": 1}
        append_to_json_array(test_file, item)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0] == item
    
    def test_append_multiple_items(self, tmp_path):
        """Test appending multiple items sequentially."""
        test_file = tmp_path / "multi.json"
        
        items = [{"id": i} for i in range(5)]
        for item in items:
            append_to_json_array(test_file, item)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 5
        assert data == items


class TestSafeReadJson:
    """Tests for safe_read_json function."""
    
    def test_safe_read_valid_json(self, tmp_path):
        """Test safe reading of valid JSON."""
        test_file = tmp_path / "valid.json"
        test_data = {"safe": "read"}
        
        write_json(test_file, test_data)
        
        result = safe_read_json(test_file)
        assert result == test_data
    
    def test_safe_read_nonexistent_returns_default(self, tmp_path):
        """Test safe reading of nonexistent file returns default."""
        test_file = tmp_path / "nonexistent.json"
        
        result = safe_read_json(test_file)
        assert result == {}  # Default is empty dict
    
    def test_safe_read_nonexistent_custom_default(self, tmp_path):
        """Test safe reading with custom default."""
        test_file = tmp_path / "nonexistent.json"
        custom_default = {"default": "value"}
        
        result = safe_read_json(test_file, default=custom_default)
        assert result == custom_default
    
    def test_safe_read_invalid_json_returns_default(self, tmp_path):
        """Test safe reading of invalid JSON returns default."""
        test_file = tmp_path / "invalid.json"
        
        with open(test_file, 'w') as f:
            f.write("invalid json {{{")
        
        result = safe_read_json(test_file, default=None)
        assert result is None
    
    def test_safe_read_none_default(self, tmp_path):
        """Test safe reading with None as default."""
        test_file = tmp_path / "nonexistent.json"
        
        result = safe_read_json(test_file, default=None)
        assert result is None
