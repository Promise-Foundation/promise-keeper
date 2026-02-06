@phase0 @api
Feature: API Agent exposes signed, policy-enforced interfaces
  Background:
    Given a Registry service exists
    And a Forwarder service exists
    And an Access Control Agent exists
    And a Consent Ledger Agent exists
    And a Storage Agent exists
    And a Coordination Agent exists
    And an API Agent exists
    And the API Agent publishes a versioned schema with a content-addressable ID
    And the API Agent verifies request signatures and enforces authentication and authorization
    And the API Agent emits standardized events and failure events

  Scenario: API Agent publishes a signed API schema and registers capability domains
    When the API Agent publishes its schema as CID "CID_API_SCHEMA_v1"
    Then the schema is cryptographically signed by the API Agent
    And the API Agent registers with the Coordination Agent offering promise domains:
      | domain               |
      | /api/query           |
      | /api/resolve         |
      | /api/storage/put     |
      | /api/storage/get     |
      | /api/evidence/submit |
    And the API Agent emits event "API_SCHEMA_PUBLISHED" referencing "CID_API_SCHEMA_v1"

  Scenario: Resolve an agent to its latest head state via the API Agent
    Given agent "AgentA" has head state "S2" in the Forwarder
    When requestor "Client" calls API endpoint "GET /resolve/AgentA"
    Then the API Agent returns a response containing resolved state "S2"
    And the response is signed by the API Agent
    And the API Agent emits event "API_RESOLVE" referencing "AgentA" and "S2"

  Scenario: Accept a signed request from an authenticated agent principal
    Given an agent principal "Client" with key pair exists
    And "Client" sends a request with a valid signature and nonce
    When the API Agent verifies the signature and nonce
    Then the API Agent accepts the request
    And emits event "API_AUTH_OK" referencing principal "Client"

  @phase1
  Scenario: Reject replayed requests
    Given an agent principal "Client" with key pair exists
    And "Client" sent a request with nonce "N1" that was accepted
    When "Client" sends the same request again with nonce "N1"
    Then the API Agent rejects the request with reason "REPLAY_DETECTED"
    And emits failure event "REFUSAL" with reason_code "REPLAY_DETECTED"

  @phase1
  Scenario: Enforce per-principal rate limits and quotas
    Given principal "Client" exceeds its configured request-per-minute limit
    When "Client" calls "POST /storage/put"
    Then the API Agent rejects with reason "RATE_LIMITED"
    And emits failure event "ACCESS_DENIED" with reason_code "RATE_LIMITED"

  Scenario: Store content via the API Agent as a gateway to the Storage Agent
    Given principal "Client" is authorized for domain "/api/storage/put"
    And "Client" sends bytes "B1" with metadata "M1"
    When "Client" calls "POST /storage/put"
    Then the API Agent forwards the request to the Storage Agent
    And the Storage Agent returns CID "CID_B1"
    And the API Agent returns "CID_B1" to "Client" in a signed response
    And the API Agent emits event "API_STORAGE_PUT" referencing "CID_B1" and principal "Client"

  Scenario: Retrieve content via the API Agent with authorization checks
    Given content "CID_B1" exists in the Storage Agent
    And principal "Client" is authorized for domain "/api/storage/get"
    When "Client" calls "GET /storage/get/CID_B1"
    Then the API Agent checks authorization via the Access Control Agent
    And the API Agent retrieves bytes from the Storage Agent
    And returns bytes to "Client" with an integrity proof referencing "CID_B1"
    And emits event "API_STORAGE_GET" referencing "CID_B1" and principal "Client"

  @phase1
  Scenario: Consent-gated access is enforced for sensitive evidence
    Given content "CID_S1" is labeled "SENSITIVE" with subject_agent_ID "HumanA"
    And principal "Client" requests purpose "assessment_review"
    And no consent exists granting "Client" access for that purpose
    When "Client" calls "GET /storage/get/CID_S1?purpose=assessment_review"
    Then the API Agent rejects with reason "CONSENT_REQUIRED"
    And emits failure event "ACCESS_DENIED" with reason_code "CONSENT_REQUIRED"

  @phase1
  Scenario: Purpose is bound into authorization decisions and audit logs
    Given content "CID_S1" is labeled "SENSITIVE" with subject_agent_ID "HumanA"
    And consent exists granting principal "Client" access for purpose "assessment_review"
    When "Client" calls "GET /storage/get/CID_S1?purpose=assessment_review"
    Then the API Agent returns the content
    And the API Agent emits event "API_ACCESS_AUDIT" including purpose "assessment_review"
    And the event is signed and includes requestor "Client" and resource "CID_S1"

  Scenario: Discover agents by promise domain through the API Agent
    Given the Coordination Agent has registered agents offering domain "/evidence/submit"
    When principal "Client" calls "GET /discover?domain=/evidence/submit"
    Then the API Agent returns a list of matching agent identifiers and head states
    And the response is signed by the API Agent

  Scenario: Submit evidence via the API Agent to the Evidence subsystem
    Given principal "Client" is authorized for domain "/api/evidence/submit"
    And "Client" has stored an artifact as CID "CID_DELIV1"
    And "Client" prepares an evidence entry referencing "CID_DELIV1"
    When "Client" calls "POST /evidence/submit" with the evidence entry
    Then the API Agent validates the evidence schema version and required fields
    And forwards the evidence submission to the Evidence Agent
    And the Evidence Agent returns evidence entry CID "CID_E1"
    And the API Agent returns "CID_E1" in a signed response
    And emits event "API_EVIDENCE_SUBMIT" referencing "CID_E1" and principal "Client"

  @phase1
  Scenario: Reject evidence submissions with unsupported schema versions
    Given principal "Client" submits evidence with schema_version "99.0"
    When "Client" calls "POST /evidence/submit"
    Then the API Agent rejects with reason "UNSUPPORTED_SCHEMA_VERSION"
    And emits failure event "REFUSAL" with reason_code "UNSUPPORTED_SCHEMA_VERSION"

  @phase1
  Scenario: API Agent emits standardized failure events
    Given principal "Client" calls an endpoint requiring authorization without permission
    When the API Agent evaluates the request
    Then the API Agent emits standardized failure event "ACCESS_DENIED"
    And the failure event includes reason_code "NOT_AUTHORIZED" and relevant context
    And the API Agent returns an error response containing the same reason_code

  @phase1
  Scenario: API Agent upgrades are forward-resolved without breaking clients
    Given API Agent "ApiA" has head state "S1"
    And API Agent "ApiA" publishes an update state "S2" referencing previous "S1"
    And the Registry emits REGISTER for "S2" and a FORWARD from "S1" to "S2"
    When a client resolves "ApiA" through the Forwarder
    Then the Forwarder returns head state "S2"
    And subsequent calls use the updated schema CID published by "S2"
