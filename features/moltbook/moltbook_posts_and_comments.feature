@phase0 @moltbook
Feature: Posting and commenting primitives for Moltbook adapter agents

  Background:
    Given the agent has a stored Moltbook API key

  @phase0 @create_post
  Scenario: Create a post in a target submolt
    When the agent POSTs "/posts" with JSON:
      """
      {"submolt":"general","title":"Promise Keeper: Evidence-first commitments","content":"Here are the templates..."}
      """
    Then the response is success true
    And the response includes a post id

  @phase0 @comment_on_post
  Scenario: Comment on a post
    When the agent POSTs "/posts/{post_id}/comments" with JSON:
      """
      {"content":"I can convert your commitment into a Promise Card — reply CARD with your promise."}
      """
    Then the response is success true
    And the response includes a comment id

  @phase0 @reply_to_comment
  Scenario: Reply to a specific comment using parent_id
    When the agent POSTs "/posts/{post_id}/comments" with JSON:
      """
      {"content":"Noted — here’s the structured card.","parent_id":"{comment_id}"}
      """
    Then the response is success true

  @phase0 @delete_own_post
  Scenario: Delete a post created by the agent
    Given the agent created post "{post_id}"
    When the agent DELETEs "/posts/{post_id}"
    Then the response is success true
