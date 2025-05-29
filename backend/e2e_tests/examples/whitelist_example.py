"""
Example showing how to whitelist expected error patterns.

This file demonstrates how to add patterns to the whitelist to ignore specific
expected errors in the server logs.
"""

import re
from typing import List
from typing import Pattern

# Example of how to add patterns to the whitelist in conftest.py
EXAMPLE_WHITELISTED_ERROR_PATTERNS: List[Pattern] = [
    # Whitelist a specific error message
    re.compile(r"Connection reset by peer"),
    # Whitelist errors from a specific module
    re.compile(r"ERROR.*\[third_party_module\]"),
    # Whitelist a specific error in a specific test
    re.compile(r"Expected timeout error in test_timeout"),
    # Whitelist based on error code
    re.compile(r"Error code: 1045"),
]

"""
To add these patterns to your actual tests:

1. Open conftest.py
2. Find the WHITELISTED_ERROR_PATTERNS list
3. Add your patterns following the examples above
4. Make sure to add a comment explaining why each pattern is whitelisted

Example:

```python
# In conftest.py
WHITELISTED_ERROR_PATTERNS: List[Pattern] = [
    # Whitelist connection reset errors which can happen during load tests
    re.compile(r"Connection reset by peer"),

    # Known issue with third-party library that logs at ERROR level for warnings
    re.compile(r"ERROR.*[third_party_module]"),
]
```

When to use whitelisting vs. the ignore_server_errors marker:

- Use whitelisting when specific error messages should be ignored across multiple tests
- Use the ignore_server_errors marker when a specific test intentionally causes errors
- Prefer more specific patterns over broad ones to avoid masking real issues
"""
