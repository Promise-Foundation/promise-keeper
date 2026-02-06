@phase0 @storage
Feature: Storage Agent provides content-addressable evidence storage
  Background:
    Given a Registry service exists
    And a Forwarder service exists
    And an Evidence Agent exists
    And a Consent Ledger Agent exists
    And a Storage Agent exists
    And the Storage Agent uses content-addressable IDs derived from canonical bytes
    And the Storage Agent validates request signatures and enforces access policies
    And the Storage Agent emits standardized events on state change and failures

  Scenario: Store and retrieve bytes by CID
    Given an authorized agent "Uploader" with key pair exists
    And "Uploader" has a signed request to store bytes "B1"
    When "Uploader" stores "B1" with the Storage Agent
    Then the Storage Agent returns CID "CID_B1"
    And the Storage Agent emits event "STORAGE_PUT" referencing "CID_B1" and attester "Uploader"
    When an authorized agent "Reader" requests bytes for "CID_B1"
    Then the Storage Agent returns bytes equal to "B1"
    And the Storage Agent emits event "STORAGE_GET" referencing "CID_B1" and requestor "Reader"

  Scenario: Storing identical bytes is idempotent
    Given an authorized agent "Uploader" with key pair exists
    And "Uploader" has bytes "B1"
    When "Uploader" stores "B1" with the Storage Agent twice
    Then both responses return the same CID "CID_B1"
    And the Storage Agent does not create divergent objects for identical content

  Scenario: Canonicalization ensures stable CIDs for structured evidence payloads
    Given an authorized agent "Uploader" with key pair exists
    And "Uploader" has a JSON evidence payload "J1" whose semantic content is unchanged by field order
    When "Uploader" stores canonicalized "J1" with the Storage Agent
    Then the Storage Agent returns CID "CID_J1"
    And a semantically identical JSON payload "J1_permuted" yields the same CID "CID_J1"

  Scenario: Retrieved content is integrity-verified
    Given an authorized agent "Uploader" stored bytes "B1" and received CID "CID_B1"
    When an authorized agent "Reader" retrieves "CID_B1"
    Then the Storage Agent verifies the bytes hash to "CID_B1" before returning
    And if verification fails the Storage Agent emits failure event "INTEGRITY_MISMATCH"

  Scenario: Store a deliverable and attach an evidence pointer entry
    Given an authorized agent "Uploader" with key pair exists
    And an Evidence Agent schema exists for evidence_type "deliverable_artifact_pointer"
    When "Uploader" stores bytes "DELIV1" with the Storage Agent
    Then the Storage Agent returns CID "CID_DELIV1"
    When "Uploader" submits an evidence entry to the Evidence Agent referencing "CID_DELIV1"
    Then the evidence entry is accepted and signed by "Uploader"
    And the evidence entry references "CID_DELIV1" as evidence_content_or_pointer

  @phase1
  Scenario: Access is denied without valid consent for sensitive content
    Given an authorized agent "Uploader" with key pair exists
    And "Uploader" labels stored content as "SENSITIVE" with subject_agent_ID "HumanA"
    And no active consent exists for requestor "Reader" to access "HumanA" sensitive evidence
    When "Reader" requests bytes for the sensitive CID
    Then the Storage Agent denies the request with reason "CONSENT_REQUIRED"
    And the Storage Agent emits failure event "ACCESS_DENIED" with reason_code "CONSENT_REQUIRED"

  @phase1
  Scenario: Access is allowed when consent is granted
    Given sensitive content exists with subject_agent_ID "HumanA" stored as CID "CID_S1"
    And the Consent Ledger Agent records consent granting "Reader" access to purpose "assessment_review" for duration "D"
    When "Reader" requests bytes for "CID_S1" with purpose "assessment_review"
    Then the Storage Agent returns the bytes
    And the Storage Agent emits event "STORAGE_GET" including purpose "assessment_review"

  @phase1
  Scenario: Purpose-bound access is enforced
    Given sensitive content exists with subject_agent_ID "HumanA" stored as CID "CID_S1"
    And consent exists granting "Reader" access only for purpose "assessment_review"
    When "Reader" requests bytes for "CID_S1" with purpose "model_training"
    Then the Storage Agent denies the request with reason "PURPOSE_NOT_AUTHORIZED"
    And the Storage Agent emits failure event "ACCESS_DENIED" with reason_code "PURPOSE_NOT_AUTHORIZED"

  @phase1
  Scenario: Maintain an append-only manifest of storage operations for audit
    Given an authorized agent "Uploader" stored bytes "B1" as CID "CID_B1"
    When the Storage Agent records this operation in its audit manifest
    Then the manifest entry is append-only and content-addressed
    And the manifest entry references "CID_B1", operation "PUT", and attester "Uploader"
    And the manifest entry is cryptographically signed by the Storage Agent

  @phase1
  Scenario: Enforce retention windows and deletion as tombstoning
    Given content "CID_B1" has retention policy "retain_for_30_days"
    When an authorized agent requests deletion of "CID_B1" before retention expiry
    Then the Storage Agent refuses with reason "RETENTION_ACTIVE"
    And emits failure event "REFUSAL" with reason_code "RETENTION_ACTIVE"
    When retention expires and deletion is requested
    Then the Storage Agent records a tombstone for "CID_B1"
    And subsequent GET requests for "CID_B1" return "TOMBSTONED" without content
    And the tombstone is signed and content-addressed

  @phase1
  Scenario: Rate limits protect the Storage Agent from abuse
    Given requestor "Reader" exceeds configured GET rate limits
    When "Reader" requests another GET for CID "CID_B1"
    Then the Storage Agent rejects with reason "RATE_LIMITED"
    And emits failure event "ACCESS_DENIED" with reason_code "RATE_LIMITED"

  @phase1
  Scenario: Reject unauthenticated store request
    Given an entity "EntityX" without a valid key pair exists
    When "EntityX" attempts to store bytes "B1"
    Then the Storage Agent rejects the request with reason "AUTHENTICATION_FAILED"
    And emits failure event "REFUSAL" with reason_code "AUTHENTICATION_FAILED"

  @phase1
  Scenario: Resolve latest Storage Agent state via Forwarder
    Given Storage Agent "StorageA" has head state "S1"
    And Storage Agent "StorageA" updates to state "S2" referencing previous "S1"
    When a requestor resolves "StorageA" through the Forwarder
    Then the Forwarder returns state "S2"
    And the requestor uses "S2" service endpoints for subsequent calls
