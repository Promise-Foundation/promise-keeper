@phase0 @runtime
Feature: Runtime heartbeat loop
  Background:
    Given the runtime heartbeat interval is 30 minutes

  Scenario: Skip when interval has not elapsed
    Given lastMoltbookCheck is 10 minutes ago
    When the runtime heartbeat loop runs
    Then the runtime skips feed checks

  Scenario: Run when interval has elapsed
    Given lastMoltbookCheck is 31 minutes ago
    When the runtime heartbeat loop runs
    Then the runtime fetches the feed endpoints
    And the runtime performs semantic search
    And the runtime updates lastMoltbookCheck
