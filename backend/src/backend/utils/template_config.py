# Standard library imports
from pathlib import Path

# Define templates directory
BASE_DIR = Path("src/backend")
TEMPLATES_DIR = BASE_DIR / "templates"

# Define the templates directory as a string for Jinja2Templates
TEMPLATES_DIR_STR = str(TEMPLATES_DIR)
