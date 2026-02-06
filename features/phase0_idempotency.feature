@phase0 @idempotency
Feature: Idempotent posting prevents duplicates

  Scenario: Reuse existing post_id for a known idempotency key
    Given an idempotency key "op1" mapped to post_id "post_1"
    And the social platform has 0 posts
    When the runtime attempts to create a post with idempotency key "op1"
    Then the existing post_id "post_1" is returned
    And no new post is created

  Scenario: New idempotency key creates a new post
    Given no idempotency mapping for "op2"
    And the social platform has 0 posts
    When the runtime attempts to create a post with idempotency key "op2"
    Then a new post_id is created and stored for "op2"
