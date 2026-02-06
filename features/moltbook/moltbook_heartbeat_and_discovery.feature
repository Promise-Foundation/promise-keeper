@phase0 @moltbook
Feature: Heartbeat integration, feed checks, and semantic discovery

  Background:
    Given the agent has a stored Moltbook API key
    And the system stores "lastMoltbookCheck" in heartbeat state

  @phase0 @heartbeat_gate
  Scenario: Only run Moltbook heartbeat if 30 minutes elapsed
    Given "lastMoltbookCheck" is 10 minutes ago
    When the heartbeat loop runs
    Then the system skips Moltbook checks

  @phase0 @heartbeat_run
  Scenario: Run Moltbook heartbeat after 30 minutes
    Given "lastMoltbookCheck" is 31 minutes ago
    When the heartbeat loop runs
    Then the system GETs "/heartbeat.md" without Authorization
    And the system follows the heartbeat instructions
    And the system updates "lastMoltbookCheck" to now

  @phase0 @feed_check
  Scenario Outline: Fetch a feed page and cache seen items to avoid repeat engagement
    When the system GETs "<endpoint>" with Authorization
    Then the response is success true
    And the response contains a list of posts
    And the agent stores each post id as "seen" for 7 days

    Examples:
      | endpoint                      |
      | /feed?sort=new&limit=10       |
      | /posts?sort=new&limit=10      |

  @phase0 @semantic_search
  Scenario: Use semantic search to find relevant conversations for Promise Keeper
    When the system GETs "/search?q=promise+verification+evidence&type=all&limit=20" with Authorization
    Then the response includes results with a "similarity" score
    And the agent prioritizes engagement with results where similarity >= 0.75
