@phase2 @policies
Feature: Domain weights and evidence floors
  Background:
    Given domain weight policies exist
    And evidence floor policies exist

  Scenario: Enforce evidence floors by domain
    Given a Promise Card in domain "/security/authentication" with evidence class "E2"
    When the promise is evaluated for EWRR eligibility
    Then the promise is marked "non-counting" with reason "EVIDENCE_FLOOR_NOT_MET"

  Scenario: Apply domain weights to EWRR
    Given a kept promise in domain "/security" and a kept promise in domain "/casual"
    When EWRR is computed
    Then the security promise receives a higher weight than the casual promise
