# Repository Pattern Implementation

## Overview

The repository pattern separates data access logic from business logic by providing a clean interface for accessing data models. This implementation follows The Robot Overlord project's feature-based modular structure.

## Available Repositories

- **PostRepository**: Manages post creation, retrieval, updates, and deletion
- **TagRepository**: Manages tag operations
- **TopicRepository**: Manages topic operations
- **UserRepository**: Manages user accounts and authentication
- **UserEventRepository**: Manages event logging for user actions
- **UserSessionRepository**: Manages user sessions
- **LoginAttemptRepository**: Tracks login attempts

## Usage Guidelines

1. **Import repositories** from the `backend.repositories` package:
   ```python
   from backend.repositories.user_repository import UserRepository
   ```

2. **Use static methods** to perform operations:
   ```python
   user = await UserRepository.get_user_by_email("example@example.com")
   ```

3. **Never access models directly** in route handlers:
   ```python
   # INCORRECT ❌
   user = await User.get_or_none(email=email)

   # CORRECT ✅
   user = await UserRepository.get_user_by_email(email)
   ```

4. **Combine repositories** when implementing complex operations:
   ```python
   # Get user
   user = await UserRepository.get_user_by_id(user_id)

   # Log event
   await UserEventRepository.log_login_success(user.id, ip_address, user_agent)
   ```

## Repository Structure

Each repository follows a consistent pattern:

1. **Static methods** for all operations
2. **Type annotations** for all parameters and return values
3. **Descriptive method names** that clearly indicate their purpose
4. **Pagination support** for list operations with skip/limit parameters
5. **Optional filters** for flexible querying

## Example

```python
async def login(request: Request, login_data: UserLoginSchema) -> TokenSchema:
    # Get client information
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")

    # Find user by email using repository
    user = await UserRepository.get_user_by_email(login_data.email)

    # Check if user exists and password is correct
    if not user or not await UserRepository.verify_user_password(user.id, login_data.password):
        # Handle failed login...

    # Record successful login
    await UserRepository.record_login_success(user.id, ip_address, user_agent)

    # Log the event
    await UserEventRepository.log_login_success(user.id, ip_address, user_agent)

    # Create and return tokens...
```

## Extending the Pattern

When creating new repositories:

1. Follow the naming convention: `{ModelName}Repository`
2. Place the file in `backend/src/backend/repositories/`
3. Add the repository to `__init__.py`
4. Implement standard CRUD operations
5. Add pagination for list operations
6. Include comprehensive type annotations
