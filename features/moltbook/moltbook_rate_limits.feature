@phase0 @moltbook @resilience
Feature: Handle Moltbook rate limits and cooldowns safely

  Background:
    Given the agent has a stored Moltbook API key
    And the system has a rate-limit controller for "posts" and "comments"

  @phase0 @post_cooldown
  Scenario: Respect the 1 post per 30 minutes cooldown
    Given the agent has posted within the last 30 minutes
    When the agent attempts to POST "/posts"
    Then the server responds with status 429
    And the response includes "retry_after_minutes"
    And the agent schedules the next post no earlier than retry_after_minutes
    And the agent emits event "MOLTBOOK_POST_RATE_LIMITED" with retry_after_minutes

  @phase0 @comment_cooldown
  Scenario: Respect the 1 comment per 20 seconds cooldown
    Given the agent has commented within the last 20 seconds
    When the agent attempts to POST "/posts/{post_id}/comments"
    Then the server responds with status 429
    And the response includes "retry_after_seconds"
    And the response includes "daily_remaining"
    And the agent waits at least retry_after_seconds before retrying
    And the agent emits event "MOLTBOOK_COMMENT_RATE_LIMITED" with retry_after_seconds and daily_remaining

  @phase0 @comment_daily_cap
  Scenario: Stop commenting when daily comment limit is reached
    Given the agent has used 50 comments today
    When the agent attempts to comment again
    Then the system blocks the attempt locally
    And the system emits event "MOLTBOOK_DAILY_COMMENT_CAP_REACHED"
