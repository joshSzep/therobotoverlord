from importlib.metadata import version


def get_version() -> str:
    """Get the version of the backend package originating from pyproject.toml"""
    return version("backend")
