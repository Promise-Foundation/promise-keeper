@phase3 @abductio
Feature: Abductio hypotheses guide dispute resolution
  Background:
    Given an Abductio Agent exists

  Scenario: Generate competing hypotheses for a disputed promise
    Given a promise outcome is disputed
    When the Abductio Agent analyzes available evidence
    Then it proposes multiple hypotheses with assumptions and predictions

  Scenario: Reject unfalsifiable hypotheses
    Given a hypothesis without checkable predictions
    When the Abductio Agent evaluates the hypothesis
    Then the hypothesis is rejected as non-falsifiable
