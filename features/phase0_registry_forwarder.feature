@phase0 @registry @forwarder
Feature: Registry and Forwarder resolve the latest agent state
  Background:
    Given a Registry service exists
    And a Forwarder service exists

  Scenario: Register and resolve an agent head state
    Given agent "AgentA" publishes state "S1"
    When the Registry records registration for "AgentA" and state "S1"
    Then the Forwarder resolves "AgentA" to state "S1"

  Scenario: Forwarder resolves to newest head state
    Given agent "AgentA" has head state "S1"
    And agent "AgentA" publishes a new state "S2" referencing "S1"
    When the Registry records registration for "S2" and a forward from "S1" to "S2"
    Then the Forwarder resolves "AgentA" to state "S2"
