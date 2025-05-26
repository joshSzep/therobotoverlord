# Content Structure API Documentation

This document outlines the API endpoints for managing content structure in The Robot Overlord debate platform.

## Topics

Topics are the main containers for discussions in the platform.

### List Topics

```
GET /topics/
```

Returns a paginated list of all topics.

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Topic Title",
      "description": "Topic description",
      "created_at": "2025-05-26T12:00:00Z",
      "updated_at": "2025-05-26T12:00:00Z",
      "author": {
        "id": "uuid",
        "display_name": "Author Name"
      }
    }
  ],
  "total": 10,
  "page": 1,
  "size": 10
}
```

### Get Topic

```
GET /topics/{topic_id}/
```

Returns details for a specific topic.

**Response**:
```json
{
  "id": "uuid",
  "title": "Topic Title",
  "description": "Topic description",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z",
  "author": {
    "id": "uuid",
    "display_name": "Author Name"
  }
}
```

### Create Topic

```
POST /topics/
```

Creates a new topic. Requires authentication.

**Request**:
```json
{
  "title": "New Topic Title",
  "description": "New topic description"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "New Topic Title",
  "description": "New topic description",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z",
  "author": {
    "id": "uuid",
    "display_name": "Author Name"
  }
}
```

### Update Topic

```
PUT /topics/{topic_id}/
```

Updates an existing topic. Requires authentication and ownership of the topic.

**Request**:
```json
{
  "title": "Updated Topic Title",
  "description": "Updated topic description"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "Updated Topic Title",
  "description": "Updated topic description",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z",
  "author": {
    "id": "uuid",
    "display_name": "Author Name"
  }
}
```

### Delete Topic

```
DELETE /topics/{topic_id}/
```

Deletes a topic. Requires authentication and ownership of the topic.

**Response**: 204 No Content

## Tags

Tags are used to categorize topics.

### List Tags

```
GET /tags/
```

Returns a paginated list of all tags.

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Tag Name",
      "slug": "tag-name",
      "created_at": "2025-05-26T12:00:00Z",
      "updated_at": "2025-05-26T12:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 10
}
```

### Get Tag

```
GET /tags/{tag_id}/
```

Returns details for a specific tag.

**Response**:
```json
{
  "id": "uuid",
  "name": "Tag Name",
  "slug": "tag-name",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z"
}
```

### Create Tag

```
POST /tags/
```

Creates a new tag. Requires authentication.

**Request**:
```json
{
  "name": "New Tag"
}
```

**Response**:
```json
{
  "id": "uuid",
  "name": "New Tag",
  "slug": "new-tag",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z"
}
```

### Update Tag

```
PUT /tags/{tag_id}/
```

Updates an existing tag. Requires authentication and admin privileges.

**Request**:
```json
{
  "name": "Updated Tag"
}
```

**Response**:
```json
{
  "id": "uuid",
  "name": "Updated Tag",
  "slug": "updated-tag",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z"
}
```

### Delete Tag

```
DELETE /tags/{tag_id}/
```

Deletes a tag. Requires authentication and admin privileges.

**Response**: 204 No Content

## Posts

Posts are the individual content items within topics.

### List Posts

```
GET /posts/
```

Returns a paginated list of all posts. Can be filtered by topic.

**Query Parameters**:
- `topic_id`: Filter posts by topic ID

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "content": "Post content",
      "created_at": "2025-05-26T12:00:00Z",
      "updated_at": "2025-05-26T12:00:00Z",
      "author": {
        "id": "uuid",
        "display_name": "Author Name"
      },
      "topic": {
        "id": "uuid",
        "title": "Topic Title"
      },
      "parent_post": null
    }
  ],
  "total": 10,
  "page": 1,
  "size": 10
}
```

### Get Post

```
GET /posts/{post_id}/
```

Returns details for a specific post.

**Response**:
```json
{
  "id": "uuid",
  "content": "Post content",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z",
  "author": {
    "id": "uuid",
    "display_name": "Author Name"
  },
  "topic": {
    "id": "uuid",
    "title": "Topic Title"
  },
  "parent_post": null
}
```

### Create Post

```
POST /posts/
```

Creates a new post. Requires authentication.

**Request**:
```json
{
  "content": "New post content",
  "topic_id": "uuid",
  "parent_post_id": "uuid" // Optional, for replies
}
```

**Response**:
```json
{
  "id": "uuid",
  "content": "New post content",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z",
  "author": {
    "id": "uuid",
    "display_name": "Author Name"
  },
  "topic": {
    "id": "uuid",
    "title": "Topic Title"
  },
  "parent_post": {
    "id": "uuid",
    "content": "Parent post content"
  }
}
```

### Update Post

```
PUT /posts/{post_id}/
```

Updates an existing post. Requires authentication and ownership of the post.

**Request**:
```json
{
  "content": "Updated post content"
}
```

**Response**:
```json
{
  "id": "uuid",
  "content": "Updated post content",
  "created_at": "2025-05-26T12:00:00Z",
  "updated_at": "2025-05-26T12:00:00Z",
  "author": {
    "id": "uuid",
    "display_name": "Author Name"
  },
  "topic": {
    "id": "uuid",
    "title": "Topic Title"
  },
  "parent_post": null
}
```

### Delete Post

```
DELETE /posts/{post_id}/
```

Deletes a post. Requires authentication and ownership of the post.

**Response**: 204 No Content

### Get Topic Posts

```
GET /topics/{topic_id}/posts/
```

Returns a paginated list of top-level posts for a specific topic.

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "content": "Post content",
      "created_at": "2025-05-26T12:00:00Z",
      "updated_at": "2025-05-26T12:00:00Z",
      "author": {
        "id": "uuid",
        "display_name": "Author Name"
      },
      "topic": {
        "id": "uuid",
        "title": "Topic Title"
      },
      "parent_post": null
    }
  ],
  "total": 10,
  "page": 1,
  "size": 10
}
```

### Get Post Replies

```
GET /posts/{post_id}/replies/
```

Returns a paginated list of replies to a specific post.

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "content": "Reply content",
      "created_at": "2025-05-26T12:00:00Z",
      "updated_at": "2025-05-26T12:00:00Z",
      "author": {
        "id": "uuid",
        "display_name": "Author Name"
      },
      "topic": {
        "id": "uuid",
        "title": "Topic Title"
      },
      "parent_post": {
        "id": "uuid",
        "content": "Parent post content"
      }
    }
  ],
  "total": 10,
  "page": 1,
  "size": 10
}
```
