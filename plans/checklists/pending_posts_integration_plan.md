# Pending Posts Integration Plan

## Overview
This checklist outlines the plan to integrate pending posts directly into topic views rather than maintaining separate pending posts pages. Rejected posts will continue to have their own dedicated views.

## Phase 1: Planning & Preparation

- [ ] Create a design mockup for how pending posts will appear in topic views
  - [ ] Design greyed out text styling for pending content
  - [ ] Design dithered background highlight for pending posts
  - [ ] Create/select an icon to indicate pending status (clock, "awaiting approval" badge, etc.)
  - [ ] Design Soviet-themed messaging for pending posts

- [ ] Review current database models to ensure they support this approach
  - [ ] Confirm `PendingPost` model has all necessary fields to display in topic view
  - [ ] Verify relationship between `PendingPost` and `Topic` models

## Phase 2: Topic View Modifications

- [ ] Update topic detail template to show pending posts
  - [ ] Modify `create_topic_detail_page` function to accept pending posts parameter
  - [ ] Add CSS classes for pending post styling
  - [ ] Add conditional rendering for pending posts with visual differentiation
  - [ ] Include moderation controls for admins/owners inline with pending posts

- [ ] Update topic detail route handler
  - [ ] Modify `get_topic_detail` to fetch both approved posts and user's pending posts
  - [ ] Add logic to determine if user is author of pending posts
  - [ ] Combine approved and pending posts in the response with appropriate flags

- [ ] Add moderation functionality directly to topic view
  - [ ] Create approve/reject action handlers accessible from topic view
  - [ ] Add appropriate CSRF protection for moderation actions
  - [ ] Implement feedback mechanism for moderation actions

## Phase 3: Profile Page Updates

- [ ] Update profile page to link to topics with pending posts instead of separate pending posts page
  - [ ] Modify pending submissions section to group pending posts by topic
  - [ ] Update links to point to topic pages with anchor/highlight for pending posts
  - [ ] Keep count of pending posts but change navigation behavior

## Phase 4: Clean Up Obsolete Pending Posts Code

- [ ] Identify all pending posts routes to be deprecated
  - [ ] `/html/pending-posts/` (list route)
  - [ ] `/html/pending-posts/{post_id}/` (detail route)
  - [ ] `/html/pending-posts/{post_id}/moderate/` (moderation route)

- [ ] Create deprecation plan for pending posts routes
  - [ ] Add deprecation notices/redirects to old routes
  - [ ] Set timeline for complete removal

- [ ] Remove obsolete pending posts templates
  - [ ] `dominate_templates/pending_posts/list.py`
  - [ ] `dominate_templates/pending_posts/detail.py`

- [ ] Remove obsolete pending posts routes
  - [ ] `routes/html/pending_posts/list_pending_posts.py`
  - [ ] `routes/html/pending_posts/get_pending_post.py`
  - [ ] `routes/html/pending_posts/moderate_pending_post.py`

- [ ] Clean up pending posts router registrations
  - [ ] Remove pending posts router from `routes/html/__init__.py`

## Phase 5: Maintain Rejected Posts Functionality

- [ ] Ensure rejected posts routes remain intact
  - [ ] Verify `/html/rejected-posts/` (list route) works correctly
  - [ ] Verify `/html/rejected-posts/{post_id}/` (detail route) works correctly

- [ ] Update rejected posts templates if needed
  - [ ] Fix any references to pending posts in rejected posts templates
  - [ ] Ensure proper styling and functionality

- [ ] Update profile page links to rejected posts
  - [ ] Ensure rejected posts count and links point to the dedicated rejected posts page

## Phase 6: Database Function Updates

- [ ] Update or create database functions to support integrated view
  - [ ] Create function to get pending posts by topic ID and user ID
  - [ ] Modify topic detail query to efficiently fetch both approved and pending posts
  - [ ] Ensure rejected posts database functions remain separate and functional

## Phase 7: Testing & Deployment

- [ ] Create test cases for new functionality
  - [ ] Test rendering of pending posts in topic view
  - [ ] Test moderation actions from topic view
  - [ ] Test proper access controls (users only see their own pending posts)
  - [ ] Test that rejected posts functionality remains intact

- [ ] Update documentation
  - [ ] Update API documentation to reflect changes
  - [ ] Update user guide/help text
  - [ ] Document the distinction between pending posts (integrated in topics) and rejected posts (separate view)

- [ ] Deploy changes
  - [ ] Run database migrations if needed
  - [ ] Deploy updated code
  - [ ] Monitor for any issues

## Phase 8: Follow-up

- [ ] Gather user feedback on the new integrated approach for pending posts
- [ ] Make refinements based on feedback
- [ ] Ensure rejected posts functionality meets user needs
