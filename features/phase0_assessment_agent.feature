@phase0 @assessment
Feature: Assessment Agent issues verdicts with evidence references
  Background:
    Given an Assessment Agent exists
    And evidence entries are stored by the Evidence Agent

  Scenario: Assess a kept promise with sufficient evidence
    Given a Promise Card with promise_id "P1"
    And evidence entries for "P1" satisfy success criteria
    When the Assessment Agent evaluates "P1"
    Then the Assessment Agent records verdict "kept"
    And the assessment includes evidence_cids
    And the assessment includes promiser_trust_tier

  Scenario: Mark inconclusive when evidence is insufficient
    Given a Promise Card with promise_id "P1"
    And evidence entries for "P1" are missing or ambiguous
    When the Assessment Agent evaluates "P1"
    Then the Assessment Agent records verdict "inconclusive"
