import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Any

class CodeParser:
    """Parses a Python project into a hierarchical structure using AST."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point for parsing the directory."""
        return self._parse_dir(self.root_path)

    def _parse_dir(self, current_path: Path) -> Dict[str, Any]:
        """Recursively parses directories into packages/components."""
        node = {
            "name": current_path.name,
            "type": "package" if (current_path / "__init__.py").exists() else "directory",
            "children": []
        }
        
        # Adjusting the project root name
        if current_path == self.root_path:
            node["type"] = "project"

        for item in sorted(current_path.iterdir()):
            if item.is_dir():
                if item.name.startswith(('.', '__pycache__')):
                    continue
                node["children"].append(self._parse_dir(item))
            elif item.suffix == ".py":
                if item.name == "__init__.py" and current_path != self.root_path:
                    continue
                node["children"].append(self._parse_file(item))
                
        return node

    def _parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parses a .py file into modules, classes, and methods."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module_node = {
                "name": file_path.name,
                "type": "module",
                "children": []
            }
            
            for item in tree.body:
                if isinstance(item, ast.ClassDef):
                    module_node["children"].append(self._parse_class(item))
                elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    module_node["children"].append({
                        "name": item.name,
                        "type": "function"
                    })
                    
            return module_node
        except Exception as e:
            return {"name": file_path.name, "type": "error", "message": str(e)}

    def _parse_class(self, class_def: ast.ClassDef) -> Dict[str, Any]:
        """Extracts methods from a class definition."""
        class_node = {
            "name": class_def.name,
            "type": "class",
            "children": []
        }
        
        for item in class_def.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Filter out pure constructors if desired, or keep all
                class_node["children"].append({
                    "name": item.name,
                    "type": "method"
                })
        return class_node

if __name__ == "__main__":
    # Test on sample_project
    parser = CodeParser("./sample_project")
    structure = parser.parse()
    print(json.dumps(structure, indent=2))
