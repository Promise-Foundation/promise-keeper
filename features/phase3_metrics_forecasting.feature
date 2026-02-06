@phase3 @metrics @forecasting
Feature: PKC scoring and forecasting calibration
  Background:
    Given PKC metric schema v1 is published
    And forecasting uses a proper scoring rule

  Scenario: Compute PKC score from kept and broken promises
    Given a set of kept promises with weights and quality multipliers
    And a set of broken promises with risk penalties
    When PKC score is computed
    Then score = sum(kept_weight * quality) - lambda * sum(broken_risk)

  Scenario: Update calibration using Brier score
    Given a promise with predicted P(kept) = 0.7
    And the promise outcome is "kept"
    When calibration is updated
    Then the Brier score is recorded for the forecaster
