import argparse
import sys
from pathlib import Path
from code_big_picture.parser import CodeParser
from code_big_picture.renderer import SVGRenderer

def main():
    parser = argparse.ArgumentParser(description="Code Big Picture - Visualize your Python codebase as nested boxes.")
    parser.add_argument("path", help="Path to the Python project directory")
    parser.add_argument("-o", "--output", default="code_map.html", help="Path to the output HTML file (default: code_map.html)")
    
    args = parser.parse_args()
    
    project_path = Path(args.path)
    if not project_path.exists():
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)
        
    print(f"Parsing project at: {project_path.absolute()}")
    
    # 1. Parse codebase
    code_parser = CodeParser(str(project_path))
    structure = code_parser.parse()
    
    # 2. Render to HTML
    print("Generating visualization...")
    renderer = SVGRenderer(structure)
    html_output = renderer.render()
    
    # 3. Save to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_output)
        
    print(f"Done! Created visualization at: {Path(args.output).absolute()}")

if __name__ == "__main__":
    main()
