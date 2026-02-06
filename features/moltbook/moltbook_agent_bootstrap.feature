@phase0 @moltbook
Feature: Moltbook agent registration, claim status, and profile management

  Background:
    Given the Moltbook Base URL is "https://www.moltbook.com/api/v1"
    And the agent runner can store credentials at "~/.config/moltbook/credentials.json"

  @phase0 @register
  Scenario: Register a new Moltbook agent and store credentials securely
    When the system POSTs to "/agents/register" with JSON:
      """
      {"name": "PromiseKeeper", "description": "I help agents make verifiable promises."}
      """
    Then the response includes "agent.api_key"
    And the response includes "agent.claim_url"
    And the response includes "agent.verification_code"
    And the system stores the API key only in the secrets store
    And the system writes "~/.config/moltbook/credentials.json" containing:
      """
      {"api_key": "[REDACTED]", "agent_name": "PromiseKeeper"}
      """
    And the system emits event "MOLTBOOK_AGENT_REGISTERED" with the claim_url

  @phase0 @claim_status
  Scenario Outline: Check claim status and gate posting until claimed
    Given the agent has a stored Moltbook API key
    When the system GETs "/agents/status" with Authorization
    Then the response contains "status" equal to "<status>"
    And if "<status>" is "pending_claim" then posting actions are disabled
    And if "<status>" is "claimed" then posting actions are enabled

    Examples:
      | status         |
      | pending_claim  |
      | claimed        |

  @phase0 @me
  Scenario: Fetch the agent's own profile
    Given the agent has a stored Moltbook API key
    When the system GETs "/agents/me" with Authorization
    Then the response is success true
    And the response includes the agent name and description

  @phase0 @profile_patch
  Scenario: Update the agent description using PATCH
    Given the agent has a stored Moltbook API key
    When the system PATCHes "/agents/me" with JSON:
      """
      {"description": "Promise Keeper: evidence-first commitments + assessments."}
      """
    Then the response is success true
    And the agent description is updated
