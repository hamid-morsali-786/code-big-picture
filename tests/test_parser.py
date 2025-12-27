"""Unit tests for CodeParser class."""
import pytest
import ast
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_big_picture.parser import CodeParser


class TestCodeParserInit:
    """Tests for CodeParser.__init__"""
    
    def test_init_with_valid_path_resolves_correctly(self, temp_dir):
        """Parser should resolve the path correctly."""
        parser = CodeParser(str(temp_dir))
        assert parser.root_path == temp_dir.resolve()
    
    def test_init_with_relative_path_converts_to_absolute(self):
        """Parser should convert relative paths to absolute."""
        parser = CodeParser(".")
        assert parser.root_path.is_absolute()


class TestCodeParserParse:
    """Tests for CodeParser.parse"""
    
    def test_parse_returns_project_node_for_root(self, sample_project):
        """Parse should return a project node at the root level."""
        parser = CodeParser(str(sample_project))
        result = parser.parse()
        assert result["type"] == "project"
    
    def test_parse_returns_dict_with_required_keys(self, sample_project):
        """Parse result should have name, type, and children keys."""
        parser = CodeParser(str(sample_project))
        result = parser.parse()
        assert "name" in result
        assert "type" in result
        assert "children" in result


class TestCodeParserParseDir:
    """Tests for CodeParser._parse_dir"""
    
    def test_parse_dir_identifies_package_with_init_file(self, sample_package):
        """Directory with __init__.py should be identified as package."""
        parser = CodeParser(str(sample_package))
        result = parser.parse()
        
        # Find the mypackage child
        pkg = next((c for c in result["children"] if c["name"] == "mypackage"), None)
        assert pkg is not None
        assert pkg["type"] == "package"
    
    def test_parse_dir_identifies_directory_without_init(self, sample_project):
        """Directory without __init__.py should be identified as directory."""
        parser = CodeParser(str(sample_project))
        result = parser.parse()
        
        # utils doesn't have __init__.py
        utils = next((c for c in result["children"] if c["name"] == "utils"), None)
        assert utils is not None
        assert utils["type"] == "directory"
    
    def test_parse_dir_skips_hidden_directories(self, temp_dir):
        """Hidden directories (starting with .) should be skipped."""
        hidden_dir = temp_dir / ".hidden"
        hidden_dir.mkdir()
        (hidden_dir / "secret.py").write_text("x = 1", encoding="utf-8")
        
        parser = CodeParser(str(temp_dir))
        result = parser.parse()
        
        hidden = next((c for c in result["children"] if c["name"] == ".hidden"), None)
        assert hidden is None
    
    def test_parse_dir_skips_pycache_directories(self, temp_dir):
        """__pycache__ directories should be skipped."""
        cache_dir = temp_dir / "__pycache__"
        cache_dir.mkdir()
        
        parser = CodeParser(str(temp_dir))
        result = parser.parse()
        
        cache = next((c for c in result["children"] if c["name"] == "__pycache__"), None)
        assert cache is None
    
    def test_parse_dir_skips_venv_directories(self, temp_dir):
        """venv directories should be skipped."""
        venv_dir = temp_dir / "venv"
        venv_dir.mkdir()
        (venv_dir / "something.py").write_text("x = 1", encoding="utf-8")
        
        parser = CodeParser(str(temp_dir))
        result = parser.parse()
        
        venv = next((c for c in result["children"] if c["name"] == "venv"), None)
        assert venv is None
    
    def test_parse_dir_includes_python_files(self, sample_project):
        """Python files should be included in children."""
        parser = CodeParser(str(sample_project))
        result = parser.parse()
        
        main_py = next((c for c in result["children"] if c["name"] == "main.py"), None)
        assert main_py is not None
        assert main_py["type"] == "module"
    
    def test_parse_dir_includes_markdown_files(self, sample_project):
        """Markdown files should be included as file type."""
        parser = CodeParser(str(sample_project))
        result = parser.parse()
        
        readme = next((c for c in result["children"] if c["name"] == "README.md"), None)
        assert readme is not None
        assert readme["type"] == "file"
    
    def test_parse_dir_excludes_empty_subdirectories(self, temp_dir):
        """Empty subdirectories should not be included."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        parser = CodeParser(str(temp_dir))
        result = parser.parse()
        
        empty = next((c for c in result["children"] if c["name"] == "empty"), None)
        assert empty is None


class TestCodeParserParseFile:
    """Tests for CodeParser._parse_file"""
    
    def test_parse_file_returns_module_node(self, sample_python_file):
        """Parsed file should have type 'module'."""
        parser = CodeParser(str(sample_python_file.parent))
        result = parser._parse_file(sample_python_file)
        
        assert result["type"] == "module"
        assert result["name"] == "calculator.py"
    
    def test_parse_file_extracts_classes(self, sample_python_file):
        """Classes should be extracted from the file."""
        parser = CodeParser(str(sample_python_file.parent))
        result = parser._parse_file(sample_python_file)
        
        calc = next((c for c in result["children"] if c["name"] == "Calculator"), None)
        assert calc is not None
        assert calc["type"] == "class"
    
    def test_parse_file_extracts_functions(self, sample_python_file):
        """Functions should be extracted from the file."""
        parser = CodeParser(str(sample_python_file.parent))
        result = parser._parse_file(sample_python_file)
        
        helper = next((c for c in result["children"] if c["name"] == "helper_function"), None)
        assert helper is not None
        assert helper["type"] == "function"
    
    def test_parse_file_extracts_async_functions(self, sample_python_file):
        """Async functions should be extracted."""
        parser = CodeParser(str(sample_python_file.parent))
        result = parser._parse_file(sample_python_file)
        
        async_helper = next((c for c in result["children"] if c["name"] == "async_helper"), None)
        assert async_helper is not None
        assert async_helper["type"] == "function"
    
    def test_parse_file_handles_syntax_error_gracefully(self, temp_dir):
        """Files with syntax errors should return error node."""
        bad_file = temp_dir / "bad.py"
        bad_file.write_text("def broken(", encoding="utf-8")
        
        parser = CodeParser(str(temp_dir))
        result = parser._parse_file(bad_file)
        
        assert result["type"] == "error"
        assert "message" in result


class TestCodeParserParseClass:
    """Tests for CodeParser._parse_class"""
    
    def test_parse_class_extracts_methods(self, sample_python_file):
        """Methods should be extracted from classes."""
        parser = CodeParser(str(sample_python_file.parent))
        result = parser._parse_file(sample_python_file)
        
        calc = next((c for c in result["children"] if c["name"] == "Calculator"), None)
        methods = [m["name"] for m in calc["children"]]
        
        assert "add" in methods
        assert "subtract" in methods
    
    def test_parse_class_handles_empty_class(self, temp_dir):
        """Empty classes should have no children."""
        empty_class_file = temp_dir / "empty_class.py"
        empty_class_file.write_text("class Empty: pass", encoding="utf-8")
        
        parser = CodeParser(str(temp_dir))
        result = parser._parse_file(empty_class_file)
        
        empty = next((c for c in result["children"] if c["name"] == "Empty"), None)
        assert empty is not None
        assert empty["children"] == []


class TestEdgeCases:
    """Edge case tests for CodeParser"""
    
    def test_parse_empty_directory(self, empty_project):
        """Empty directory should return project with no children."""
        parser = CodeParser(str(empty_project))
        result = parser.parse()
        
        assert result["type"] == "project"
        assert result["children"] == []
    
    def test_parse_deeply_nested_structure(self, temp_dir):
        """Parser should handle deeply nested structures."""
        # Create 10 levels of nesting
        current = temp_dir
        for i in range(10):
            current = current / f"level_{i}"
            current.mkdir()
            (current / "__init__.py").write_text("", encoding="utf-8")
        
        (current / "deep.py").write_text("def deep(): pass", encoding="utf-8")
        
        parser = CodeParser(str(temp_dir))
        result = parser.parse()
        
        # Navigate to deepest level
        node = result
        for i in range(10):
            node = next((c for c in node["children"] if c["name"] == f"level_{i}"), None)
            assert node is not None
