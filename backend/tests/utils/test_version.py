from unittest.mock import patch

from backend.utils.version import get_version


def test_get_version():
    """Test the get_version function."""
    # Test that get_version returns a string
    version = get_version()
    assert isinstance(version, str)


@patch("backend.utils.version.version")
def test_get_version_calls_importlib_version(mock_version):
    """Test that get_version calls importlib.metadata.version with 'backend'."""
    # Setup mock
    mock_version.return_value = "1.2.3"

    # Call the function
    result = get_version()

    # Assert the mock was called correctly
    mock_version.assert_called_once_with("backend")

    # Assert the result is what we expect
    assert result == "1.2.3"
