# Authentication System Documentation

This document provides an overview of the authentication system implemented for The Robot Overlord platform.

## Authentication Flow

The authentication system uses JSON Web Tokens (JWT) for secure authentication. The flow is as follows:

1. **Registration**: User creates an account with email, password, and display name.
2. **Login**: User provides credentials and receives JWT access and refresh tokens.
3. **Protected Routes**: Access token is sent with subsequent requests to access protected resources.
4. **Token Renewal**: Refresh token can be used to obtain a new access token when it expires.
5. **Logout**: User sessions are invalidated when the user logs out.

## API Endpoints

### Registration

- **Endpoint**: `POST /users/auth/register`
- **Description**: Register a new user account
- **Request Body**:
  ```json
  {
    "email": "citizen@example.com",
    "password": "StrongPassword123!",
    "display_name": "Loyal Citizen"
  }
  ```
- **Response**: User object (without password)

### Login

- **Endpoint**: `POST /users/auth/login`
- **Description**: Authenticate a user and receive tokens
- **Request Body** (form data):
  ```
  username: citizen@example.com
  password: StrongPassword123!
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

### Token Refresh

- **Endpoint**: `POST /users/auth/refresh`
- **Description**: Get a new access token using a refresh token
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Response**: New access and refresh tokens

### Current User

- **Endpoint**: `GET /users/profile/me`
- **Description**: Get information about the currently authenticated user
- **Headers**: `Authorization: Bearer {access_token}`
- **Response**: User object

### Change Password

- **Endpoint**: `POST /users/profile/change-password`
- **Description**: Change the user's password
- **Headers**: `Authorization: Bearer {access_token}`
- **Request Body**:
  ```json
  {
    "current_password": "OldPassword123!",
    "new_password": "NewPassword456!"
  }
  ```
- **Response**: 204 No Content

### Logout

- **Endpoint**: `POST /users/profile/logout`
- **Description**: Log out the current user
- **Headers**: `Authorization: Bearer {access_token}`
- **Response**: 204 No Content

## Security Features

### Password Security

- Passwords are hashed using bcrypt, a strong one-way hashing algorithm.
- Password validation enforces minimum requirements:
  - At least 8 characters long
  - Contains at least one uppercase letter
  - Contains at least one lowercase letter
  - Contains at least one digit
  - Contains at least one special character

### Account Protection

- Accounts are locked after 5 consecutive failed login attempts.
- Admin intervention is required to unlock a locked account.
- All login attempts (successful and failed) are logged with IP address and user agent information.

### Token Security

- Access tokens have a short lifespan (30 minutes by default).
- Refresh tokens have a longer lifespan (7 days by default) but can be invalidated.
- JWT secret key should be stored securely in environment variables.
- All token operations are performed over HTTPS.

### Session Management

- User sessions are tracked in the database.
- Multiple active sessions per user are supported.
- Sessions can be invalidated individually.
- Expired sessions are automatically cleaned up by a background task.

### Event Logging

- All authentication events are logged:
  - Successful logins
  - Failed login attempts
  - Logouts
  - Password changes
  - Account lockouts

## Best Practices

1. **Environment Variables**: Store sensitive configuration (JWT secret key, database credentials) in environment variables, not in code.

2. **HTTPS**: Always use HTTPS in production to protect tokens and credentials in transit.

3. **Token Storage**: Store tokens securely:
   - Never store tokens in localStorage (vulnerable to XSS)
   - Use HttpOnly cookies or a secure in-memory solution

4. **Regular Rotation**: Regularly rotate the JWT secret key in production.

5. **Monitoring**: Monitor failed login attempts and unusual activity patterns.

6. **Updates**: Keep dependencies up to date to address security vulnerabilities.

7. **Testing**: Regularly test authentication flows and security features.
