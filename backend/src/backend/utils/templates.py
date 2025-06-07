# Third-party imports
from fastapi.templating import Jinja2Templates
from jinja2 import Environment

# Project-specific imports
from backend.routes.html.utils.template_filters import setup_jinja_filters
from backend.utils.template_config import TEMPLATES_DIR_STR

# Initialize Jinja2 templates
templates: Jinja2Templates = Jinja2Templates(directory=TEMPLATES_DIR_STR)

# Set up Jinja2 filters
env: Environment = templates.env
setup_jinja_filters(env=env)  # type: ignore[reportUnknownArgumentType,unused-ignore]
