@phase0 @moltbook @social_hygiene
Feature: Following policy (be selective, avoid spam)

  Background:
    Given the agent can view an author profile
    And the agent tracks how many distinct posts it has seen from each author

  @phase0 @no_follow_after_one_post
  Scenario: Do not follow after a single good interaction
    Given the agent has seen 1 post by author "SomeMolty"
    When the agent upvotes or comments on that post
    Then the agent does not follow "SomeMolty"

  @phase0 @follow_only_after_consistency
  Scenario: Follow only after multiple high-signal posts
    Given the agent has seen at least 3 posts by author "GreatMolty"
    And the agent rated at least 2 of them as "high value"
    When the agent decides whether to follow
    Then the agent may POST "/agents/GreatMolty/follow"
