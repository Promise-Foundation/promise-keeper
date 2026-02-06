@phase0 @evidence
Feature: Evidence Agent stores evidence entries with CIDs
  Background:
    Given an Evidence Agent exists
    And evidence entries are content-addressed

  Scenario: Submit E2 evidence with artifact_cid
    Given a Promise Card with promise_id "P1"
    And an artifact_cid "CID_A1" and mirror URL "https://example/artifact"
    When the promiser submits evidence of class "E2" referencing "CID_A1"
    Then the Evidence Agent accepts the evidence entry
    And the evidence entry includes artifact_cid "CID_A1"

  Scenario: Reject E2 evidence without artifact_cid
    Given a Promise Card with promise_id "P1"
    When the promiser submits evidence of class "E2" without artifact_cid
    Then the Evidence Agent rejects the evidence entry with reason "E2_REQUIRES_CID"

  Scenario: Record E4 evidence with attestation and log inclusion proof
    Given a Promise Card with promise_id "P1"
    And an artifact_cid "CID_A1"
    And a signed attestation by "ValidatorV"
    And an append-only log inclusion proof
    When the promiser submits evidence of class "E4"
    Then the Evidence Agent accepts the evidence entry
    And stores the attestation and inclusion proof
