from backend.db.models.user_session import UserSession


async def delete_user_session(token: str) -> bool:
    # Find the session by token
    session = await UserSession.filter(session_token=token).first()

    if not session:
        return False

    # Deactivate the session
    session.is_active = False
    await session.save()

    return True
