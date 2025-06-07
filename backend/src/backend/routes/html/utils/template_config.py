# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Third-party imports
from fastapi import Request
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.utils.templates import templates


# Helper function to render templates with common context
def render_template(
    request: Request, template_name: str, context: Optional[Dict[str, Any]] = None
) -> HTMLResponse:
    # Initialize empty dict if None
    if context is None:
        context = {}

    # Add request to context (required by Jinja2Templates)
    context["request"] = request

    # Return rendered template
    return templates.TemplateResponse(template_name, context)
