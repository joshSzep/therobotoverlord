# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import ValidationError

# Project-specific imports
from backend.db.models.post import Post
from backend.db.models.topic import Topic
from backend.db.models.user import User
from backend.routes.posts.schemas import PostCreate
from backend.routes.posts.schemas import PostList
from backend.routes.posts.schemas import PostResponse
from backend.routes.posts.schemas import PostUpdate
from backend.utils.auth import get_current_user

router = APIRouter(tags=["posts"])


@router.get("/", response_model=PostList)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    topic_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
) -> PostList:
    # Build query with filters
    query = Post.all().prefetch_related("author", "topic")

    if topic_id:
        query = query.filter(topic__id=topic_id)

    if author_id:
        query = query.filter(author_id=author_id)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit)

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post
        reply_count = await Post.filter(parent_post_id=post.id).count()

        # Create response object
        post_dict = {
            "id": post.id,
            "content": post.content,
            "author": post.author,
            "topic_id": post.topic.id,
            "parent_post_id": post.parent_post.id if post.parent_post else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "reply_count": reply_count,
        }
        post_responses.append(PostResponse.model_validate(post_dict))

    return PostList(posts=post_responses, count=count)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate, current_user: User = Depends(get_current_user)
) -> PostResponse:
    # Verify that the topic exists
    topic = await Topic.get_or_none(id=post_data.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Verify that the parent post exists and belongs to the same topic if provided
    parent_post = None
    if post_data.parent_post_id:
        parent_post = await Post.get_or_none(id=post_data.parent_post_id)
        if not parent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found",
            )

        if str(parent_post.topic.id) != str(post_data.topic_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent post must belong to the same topic",
            )

    try:
        # Create the post
        post = await Post.create(
            content=post_data.content,
            author=current_user,
            topic=topic,
            parent_post=parent_post,
        )

        # Fetch related data
        await post.fetch_related("author", "topic")

        # Get reply count (should be 0 for a new post)
        reply_count = await Post.filter(parent_post=post).count()

        # Create response object
        post_dict = {
            "id": post.id,
            "content": post.content,
            "author": post.author,
            "topic_id": post.topic.id,
            "parent_post_id": post.parent_post.id if post.parent_post else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "reply_count": reply_count,
        }

        return PostResponse.model_validate(post_dict)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID) -> PostResponse:
    try:
        post = await Post.get(id=post_id).prefetch_related("author", "topic")

        # Get reply count
        reply_count = await Post.filter(parent_post=post).count()

        # Create response object
        post_dict = {
            "id": post.id,
            "content": post.content,
            "author": post.author,
            "topic_id": post.topic.id,
            "parent_post_id": post.parent_post.id if post.parent_post else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "reply_count": reply_count,
        }

        return PostResponse.model_validate(post_dict)

    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    try:
        post = await Post.get(id=post_id).prefetch_related("author", "topic")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check if the current user is the author
    if str(post.author.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this post",
        )

    # Update the post
    post.content = post_data.content
    await post.save()

    # Get reply count
    reply_count = await Post.filter(parent_post=post).count()

    # Create response object
    post_dict = {
        "id": post.id,
        "content": post.content,
        "author": post.author,
        "topic_id": post.topic.id,
        "parent_post_id": post.parent_post.id if post.parent_post else None,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "reply_count": reply_count,
    }

    return PostResponse.model_validate(post_dict)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        post = await Post.get(id=post_id).prefetch_related("author")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check if the current user is the author or an admin
    if str(post.author.id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post",
        )

    # Check if the post has replies
    reply_count = await Post.filter(parent_post=post).count()
    if reply_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete post as it has {reply_count} replies",
        )

    # Delete the post
    await post.delete()


@router.get("/topics/{topic_id}/posts/", response_model=PostList)
async def list_topic_posts(
    topic_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the topic exists
    topic = await Topic.get_or_none(id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get top-level posts (no parent post)
    query = Post.filter(topic=topic, parent_post=None)
    query = query.prefetch_related("author", "topic")

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit)

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post
        reply_count = await Post.filter(parent_post_id=post.id).count()

        # Create response object
        post_dict = {
            "id": post.id,
            "content": post.content,
            "author": post.author,
            "topic_id": post.topic.id,
            "parent_post_id": post.parent_post.id if post.parent_post else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "reply_count": reply_count,
        }
        post_responses.append(PostResponse.model_validate(post_dict))

    return PostList(posts=post_responses, count=count)


@router.get("/posts/{post_id}/replies/", response_model=PostList)
async def list_post_replies(
    post_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the parent post exists
    parent_post = await Post.get_or_none(id=post_id)
    if not parent_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent post not found",
        )

    # Get replies to the post
    query = Post.filter(parent_post=parent_post).prefetch_related("author", "topic")

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit)

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post
        reply_count = await Post.filter(parent_post_id=post.id).count()

        # Create response object
        post_dict = {
            "id": post.id,
            "content": post.content,
            "author": post.author,
            "topic_id": post.topic.id,
            "parent_post_id": post.parent_post.id if post.parent_post else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "reply_count": reply_count,
        }
        post_responses.append(PostResponse.model_validate(post_dict))

    return PostList(posts=post_responses, count=count)
