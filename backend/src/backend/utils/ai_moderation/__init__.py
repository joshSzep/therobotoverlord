from backend.utils.ai_moderation.service import AIModeratorService

# Global instance of the AI moderator service
ai_moderator_service = None


def init_ai_moderator_service() -> AIModeratorService:
    """Initialize the global AI moderator service instance"""
    global ai_moderator_service
    ai_moderator_service = AIModeratorService()
    return ai_moderator_service


def get_ai_moderator_service() -> AIModeratorService:
    """Get the global AI moderator service instance"""
    if ai_moderator_service is None:
        return init_ai_moderator_service()
    return ai_moderator_service
