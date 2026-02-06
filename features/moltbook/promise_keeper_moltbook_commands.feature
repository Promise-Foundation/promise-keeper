@phase0 @moltbook @promise_keeper
Feature: Promise Keeper social command handling on Moltbook

  Background:
    Given the agent has a stored Moltbook API key
    And the agent monitors new posts and comments for trigger phrases
    And the agent can compute content-addressed IDs (CIDs) for Promise Cards and Evidence
    And the agent stores mapping from "moltbook_post_or_comment_id" to "protocol_object_cid"

  @phase0 @card_command
  Scenario: Respond to CARD request by producing a Promise Card and posting it as a comment
    Given a Moltbook comment contains the trigger "CARD"
    And the comment contains a natural-language commitment statement
    When the agent parses the commitment statement
    Then the agent generates a Promise Card with fields:
      | from              |
      | domain            |
      | promise           |
      | success_criteria  |
      | evidence_plan     |
      | assessment_window |
      | failure_modes     |
    And the agent computes "promise_card_cid" as a hash of the normalized fields
    When the agent POSTs "/posts/{post_id}/comments" with JSON:
      """
      {"content": "<rendered_promise_card_in_markdown_including promise_card_cid>"}
      """
    Then the response is success true
    And the agent records a link between the Moltbook comment id and promise_card_cid

  @phase0 @certify_command
  Scenario: Respond to CERTIFY request by requesting evidence and scheduling assessment
    Given a Moltbook post or comment contains the trigger "CERTIFY"
    And the referenced Promise Card includes "promise_card_cid"
    When the agent receives the request
    Then the agent replies with an Evidence Request comment asking for:
      | artifact link or CID |
      | timestamps           |
      | any third-party attestations |
    And the agent opens an Assessment Window timer based on the Promise Card
    And the agent emits event "ASSESSMENT_REQUESTED" with promise_card_cid

  @phase0 @dispute_command
  Scenario: Respond to DISPUTE request by creating a Conflict record and gathering claims
    Given a Moltbook thread contains the trigger "DISPUTE"
    And the thread references a promise_card_cid
    When the agent receives the dispute trigger
    Then the agent posts the CONFLICT template as a comment
    And the agent requests each party to submit:
      | claim summary |
      | evidence pointers |
      | conflict_of_interest declaration |
    And the agent emits event "DISPUTE_OPENED" with promise_card_cid

  @phase0 @assessment_posting
  Scenario Outline: Post an Assessment Card with verdict and evidence class
    Given an assessment decision exists for promise_card_cid
    And evidence has been classified as "<evidence_class>"
    When the agent posts an Assessment Card to the Moltbook thread
    Then the Assessment Card includes:
      | verdict                   |
      | evidence pointers or CIDs |
      | rationale                 |
      | assessor name             |
      | independence statement    |
      | evidence_class            |
    And the agent stores assessment_cid and links it to the Moltbook comment id

    Examples:
      | evidence_class |
      | E0            |
      | E1            |
      | E2            |
      | E3            |
      | E4            |
