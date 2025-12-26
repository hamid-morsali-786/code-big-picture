# sample_project/main.py

from .core.engine import Engine

def main():
    """Main entry point."""
    e = Engine("Test")
    e.start()

if __name__ == "__main__":
    main()
