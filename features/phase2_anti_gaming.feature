@phase2 @anti_gaming
Feature: Anti-gaming controls for EWRR integrity
  Background:
    Given the system tracks EWRR and evidence classes
    And the system enforces rate limits for EWRR counting

  Scenario: Enforce objective markers per domain
    Given a Promise Card in domain "/software/debug" without diffstat or tests
    When the promise is evaluated for EWRR eligibility
    Then the promise is marked "non-counting" with reason "MISSING_OBJECTIVE_MARKER"

  Scenario: Aggregate repeated identical micro-promises
    Given an agent submits 10 identical promises within a day
    When the system aggregates promises for EWRR
    Then the promises count as 1 toward EWRR

  Scenario: Collusion response is staged and non-punitive first
    Given a validator "V1" assesses 85 percent of "A1" promises
    When collusion detection thresholds are crossed
    Then the system increases meta-review sampling
    And requires external validator sampling
    And only downweights if evidence quality diverges over time
