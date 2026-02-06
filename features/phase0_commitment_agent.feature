@phase0 @commitment
Feature: Commitment Agent records promises with canonical IDs
  Background:
    Given a Commitment Agent exists
    And canonical Promise Card rules exist

  Scenario: Record a new Promise Card
    Given a Promise Card from "AgentA" in domain "/software/debug"
    When the Commitment Agent validates required fields
    Then the Commitment Agent stores the Promise Card
    And the Commitment Agent returns the promise_id

  Scenario: Reject Promise Cards missing required fields
    Given a Promise Card missing "evidence_plan"
    When the Commitment Agent validates the Promise Card
    Then the Commitment Agent rejects the Promise Card with reason "MISSING_REQUIRED_FIELDS"
