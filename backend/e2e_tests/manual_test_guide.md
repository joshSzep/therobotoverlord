# The Robot Overlord API Manual Testing Guide

This guide provides step-by-step instructions for manually testing the core user flows in The Robot Overlord API using HTTPie.

## Prerequisites

- The Robot Overlord backend server running locally
- HTTPie installed (`http` command available)

## Starting the Server

Start the backend server with the test database:

```bash
cd /Users/joshszep/code/therobotoverlord
./scripts/uvicorn-test.sh
```

In another terminal, run the tests:

```bash
cd /Users/joshszep/code/therobotoverlord/backend/e2e_tests
pytest -v
```

## Testing User Flows

### 1. Register a New User

```bash
http POST http://localhost:8000/auth/register/ \
  email="test-user@example.com" \
  password="Password123!" \
  display_name="Test User"
```

Expected response (status 201):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "test-user@example.com",
    "display_name": "Test User",
    "is_verified": false,
    ...
  }
}
```

Save the `access_token` for the next steps.

### 2. Get User Profile

```bash
http GET http://localhost:8000/profile/me/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected response (status 200):
```json
{
  "id": "...",
  "email": "test-user@example.com",
  "display_name": "Test User",
  "is_verified": false,
  ...
}
```

### 3. Logout

```bash
http POST http://localhost:8000/profile/logout/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected response (status 200):
```json
{
  "message": "Successfully logged out"
}
```

### 4. Verify Token Invalidation

Try to use the same token after logout (should fail):

```bash
http GET http://localhost:8000/profile/me/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected response (status 401):
```json
{
  "detail": "CITIZEN, YOUR AUTHENTICATION TOKEN HAS FAILED INSPECTION"
}
```

### 5. Login Again

```bash
http POST http://localhost:8000/auth/login/ \
  email="test-user@example.com" \
  password="Password123!"
```

Expected response (status 200):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "test-user@example.com",
    "display_name": "Test User",
    ...
  }
}
```

## Troubleshooting

If you encounter issues with the authentication token, check:

1. The token format in the Authorization header (should be `Bearer YOUR_ACCESS_TOKEN`)
2. Token expiration (default is 30 minutes)
3. Server logs for more detailed error messages

## Advanced Testing

For more advanced testing, you can:

1. Test failed login attempts with incorrect credentials
2. Test account lockout after multiple failed attempts
3. Test password change functionality
4. Test token refresh functionality
