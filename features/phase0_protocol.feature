@phase0 @protocol
Feature: Canonical cards, IDs, and revision semantics
  Background:
    Given canonicalization rules for card fields exist
    And content IDs (CIDs) are computed from canonical bytes
    And signatures are optional in Phase 0 and expected by Phase 2

  Scenario: Create a Promise Card with a canonical promise_id
    Given a promiser "AgentA"
    And a Promise Card with required fields and evidence_plan
    When the Promise Card is canonicalized and hashed
    Then a promise_id CID is produced
    And the promise_id is included in the Promise Card

  Scenario: Promise revisions preserve history
    Given a Promise Card with promise_id "P1"
    When the promiser issues a revision with previous_promise_id "P1"
    Then the new Promise Card has a new promise_id "P2"
    And the revision chain includes "P1" -> "P2"
    And the original Promise Card remains immutable

  Scenario: Cancellation is recorded and visible
    Given a Promise Card with promise_id "P1" and assessment_window "W1"
    When the promiser publishes a cancellation notice for "P1"
    Then the cancellation notice is recorded with reason and timestamp
    And the cancellation is visible in the promiser's EWRR
