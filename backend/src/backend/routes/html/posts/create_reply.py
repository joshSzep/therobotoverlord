import logging
from typing import Annotated
from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import RedirectResponse

from backend.db_functions.posts.create_post import create_post
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional


async def create_reply_handler(
    request: Request,
    current_user: Annotated[Optional[UserResponse], Depends(get_current_user_optional)],
    topic_id: str = Form(...),
    parent_post_id: str = Form(...),
    content: str = Form(...),
) -> Response:
    """
    Handle the creation of a reply to a post.
    """
    # Check if user is authenticated
    if not current_user:
        return RedirectResponse(
            url="/html/auth/login/", status_code=status.HTTP_303_SEE_OTHER
        )

    # Debug logging
    logging.debug(f"Reply form submission: topic_id={topic_id}")
    logging.debug(f"parent_post_id={parent_post_id}")
    logging.debug(f"Content: {content}")

    try:
        # Convert string IDs to UUID
        topic_uuid = UUID(topic_id)
        parent_post_uuid = UUID(parent_post_id)

        logging.debug(f"Converted UUIDs: topic_uuid={topic_uuid}")
        logging.debug(f"parent_post_uuid={parent_post_uuid}")

        # Create the reply post
        await create_post(
            author_id=current_user.id,
            topic_id=topic_uuid,
            content=content,
            parent_post_id=parent_post_uuid,
        )

        # Redirect to the topic page
        return RedirectResponse(
            url=f"/html/topics/{topic_uuid}/",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except ValueError:
        # Handle invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid topic_id or parent_post_id format",
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
