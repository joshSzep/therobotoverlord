"""
Data access functions for The Robot Overlord.

This module provides direct data access functions for database operations.
Each function is responsible for a specific database operation and returns
a Pydantic schema object.

Key principles:
- Functions return Pydantic schemas, not ORM models (Rule #5)
- Function names follow consistent patterns (Rule #6):
  - get_*_by_id: Retrieve a single item by ID
  - list_*: Return a paginated list of items
  - create_*: Create a new item
  - update_*: Update an existing item
  - delete_*: Delete an item
- Functions use converters to transform ORM models to Pydantic schemas
"""
