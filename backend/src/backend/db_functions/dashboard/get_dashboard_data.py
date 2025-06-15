# Standard library imports
from typing import Dict
from typing import List
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.converters.post_to_schema import post_to_schema
from backend.converters.rejected_post_to_schema import rejected_post_to_schema
from backend.db.models.ai_analysis import AIAnalysis
from backend.db.models.post import Post
from backend.db.models.rejected_post import RejectedPost
from backend.schemas.ai_analysis import AIAnalysisResponse
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse
from backend.schemas.rejected_post import RejectedPostList
from backend.schemas.rejected_post import RejectedPostResponse


async def get_dashboard_data(
    skip: int = 0,
    limit: int = 10,
) -> Tuple[PostList, RejectedPostList, Dict[UUID, AIAnalysisResponse]]:
    """
    Get all posts (approved and rejected) with AI analysis for the dashboard.

    Returns a tuple containing:
    - PostList of approved posts
    - RejectedPostList of rejected posts
    - Dictionary mapping post IDs to their AI analysis
    """
    # Fetch approved posts with pagination
    posts = (
        await Post.all().prefetch_related("author", "topic").offset(skip).limit(limit)
    )
    total_posts = await Post.all().count()

    # Convert to schema objects using the converter
    post_responses: List[PostResponse] = []
    for post in posts:
        post_schema = await post_to_schema(post)
        post_responses.append(post_schema)

    # Fetch rejected posts with pagination
    rejected_posts = (
        await RejectedPost.all()
        .prefetch_related("author", "topic")
        .offset(skip)
        .limit(limit)
    )
    total_rejected_posts = await RejectedPost.all().count()

    # Convert to schema objects using the converter
    rejected_post_responses: List[RejectedPostResponse] = []
    for rejected_post in rejected_posts:
        rejected_schema = await rejected_post_to_schema(rejected_post)
        rejected_post_responses.append(rejected_schema)

    # Create the response objects
    posts_list = PostList(posts=post_responses, count=total_posts)
    rejected_posts_list = RejectedPostList(
        rejected_posts=rejected_post_responses, count=total_rejected_posts
    )

    # Fetch AI analysis for all posts
    # Since AI analysis is linked to pending posts, we need to:
    # 1. Get all the pending post IDs that were eventually approved or rejected
    # 2. Fetch AI analysis for those pending post IDs
    # 3. Create a mapping from post ID to AI analysis

    # Get all post IDs
    # Note: This is a simplified approach. In a real implementation, we would need
    # to track the relationship between pending/approved/rejected posts.
    approved_post_ids = [post.id for post in post_responses]
    rejected_post_ids = [post.id for post in rejected_post_responses]
    all_post_ids = approved_post_ids + rejected_post_ids

    # Fetch AI analyses for these posts
    # We assume the pending_post_id field in AIAnalysis corresponds to
    # either an approved post ID or a rejected post ID
    ai_analyses = await AIAnalysis.all().prefetch_related("pending_post")

    # Create a mapping of post ID to AI analysis
    ai_analysis_map: Dict[UUID, AIAnalysisResponse] = {}
    for analysis in ai_analyses:
        # Check if this analysis is related to one of our posts
        if analysis.pending_post and analysis.pending_post.id in all_post_ids:
            ai_analysis_map[analysis.pending_post.id] = AIAnalysisResponse(
                id=analysis.id,
                pending_post_id=analysis.pending_post.id,
                decision=analysis.decision,
                confidence_score=analysis.confidence_score,
                analysis_text=analysis.analysis_text,
                feedback_text=analysis.feedback_text,
                processing_time_ms=analysis.processing_time_ms,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at,
            )

    return posts_list, rejected_posts_list, ai_analysis_map
