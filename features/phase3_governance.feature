@phase3 @governance
Feature: PKC governance for policy evolution
  Background:
    Given PKC members exist
    And governance proposals are versioned and signed

  Scenario: Run a governance proposal with notice and vote
    Given a policy proposal with comment period of 7 days
    When the vote period opens
    Then members may vote YES, NO, or ABSTAIN
    And the proposal passes only if threshold is met

  Scenario: Enforce vote weight caps
    Given a member has high PKC score
    When vote weights are computed
    Then no single member exceeds 5 percent vote weight

  Scenario: Roll back a policy after regressions
    Given a policy change causes measurable regressions
    When the rollback plan is invoked
    Then the prior policy version is restored
