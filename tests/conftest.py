"""Shared pytest fixtures for Code Big Picture tests."""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Creates a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_python_file(temp_dir):
    """Creates a sample Python file with class and function."""
    content = '''
class Calculator:
    """A simple calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

def helper_function():
    """A standalone function."""
    pass

async def async_helper():
    """An async function."""
    pass
'''
    file_path = temp_dir / "calculator.py"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_package(temp_dir):
    """Creates a sample Python package structure."""
    # Create package directory
    pkg_dir = temp_dir / "mypackage"
    pkg_dir.mkdir()
    
    # Add __init__.py to make it a package
    (pkg_dir / "__init__.py").write_text("# Package init", encoding="utf-8")
    
    # Add a module
    module_content = '''
class Service:
    def run(self):
        pass
'''
    (pkg_dir / "service.py").write_text(module_content, encoding="utf-8")
    
    return temp_dir


@pytest.fixture
def sample_project(temp_dir):
    """Creates a complete sample project structure."""
    # Root level files
    (temp_dir / "main.py").write_text("def main(): pass", encoding="utf-8")
    (temp_dir / "README.md").write_text("# Project", encoding="utf-8")
    
    # src package
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "core.py").write_text("class Core: pass", encoding="utf-8")
    
    # utils directory (not a package)
    utils_dir = temp_dir / "utils"
    utils_dir.mkdir()
    (utils_dir / "helpers.py").write_text("def helper(): pass", encoding="utf-8")
    
    return temp_dir


@pytest.fixture
def empty_project(temp_dir):
    """Creates an empty project directory."""
    return temp_dir


@pytest.fixture
def simple_structure():
    """Returns a simple node structure for renderer tests."""
    return {
        "name": "TestProject",
        "type": "project",
        "children": [
            {
                "name": "module.py",
                "type": "module",
                "children": [
                    {"name": "MyClass", "type": "class", "children": [
                        {"name": "__init__", "type": "method"},
                        {"name": "run", "type": "method"}
                    ]},
                    {"name": "helper", "type": "function"}
                ]
            }
        ]
    }


@pytest.fixture
def empty_structure():
    """Returns an empty project structure."""
    return {
        "name": "EmptyProject",
        "type": "project",
        "children": []
    }


@pytest.fixture
def deeply_nested_structure():
    """Returns a deeply nested structure for stress testing."""
    def create_level(depth, max_depth=5):
        if depth >= max_depth:
            return {"name": f"leaf_{depth}", "type": "function"}
        return {
            "name": f"level_{depth}",
            "type": "package" if depth < 3 else "class",
            "children": [create_level(depth + 1, max_depth)]
        }
    
    return {
        "name": "DeepProject",
        "type": "project",
        "children": [create_level(0)]
    }
