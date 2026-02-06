@phase1 @validators
Feature: Validator circle with auditable assignment and meta-review
  Background:
    Given a Validator Pool exists
    And a deterministic assignment rule exists

  Scenario: Assign validators deterministically for CERTIFY
    Given a Promise Card with promise_id "P1"
    And a validator pool snapshot "POOL_V1" with N validators
    And an epoch_id "E1"
    When a CERTIFY request is issued
    Then validator_index = H("P1" || "E1" || "POOL_V1") mod N is selected
    And the selected validator is returned with the CERTIFY response

  Scenario: Meta-review sampling is applied
    Given an assessment for promise_id "P1" by validator "V1"
    When the system applies meta-review sampling at 10 percent
    Then a second validator may be assigned for review
    And discrepancies are recorded for escalation

  Scenario: Weekly batch report includes validator performance
    Given multiple assessments completed in the last week
    When the system generates the weekly digest
    Then the report includes kept, broken, and inconclusive counts
    And the report includes validator response times and dispute rates
