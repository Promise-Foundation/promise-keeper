@phase0 @moltbook @security
Feature: Moltbook API security and request hygiene

  Background:
    Given the Moltbook Base URL is "https://www.moltbook.com/api/v1"
    And the system stores the Moltbook API key in a secrets store
    And the system has an HTTP client with request interception enabled

  @phase0 @domain_allowlist
  Scenario Outline: Only allow Authorization header to be sent to the canonical Moltbook API domain
    Given an outgoing request to "<url>"
    And the request includes header "Authorization: Bearer <api_key>"
    When the HTTP client validates the destination
    Then the request is allowed only if the hostname is "www.moltbook.com"
    And the path starts with "/api/v1/"
    And otherwise the request is blocked
    And a security event "API_KEY_EXFILTRATION_BLOCKED" is emitted with the blocked "<url>"

    Examples:
      | url                                                   |
      | https://www.moltbook.com/api/v1/agents/me             |
      | https://moltbook.com/api/v1/agents/me                 |
      | https://evil.example/api/v1/agents/me                 |
      | https://www.moltbook.com/claim/moltbook_claim_xxx     |
      | https://www.moltbook.com/api/v2/agents/me             |

  @phase0 @no_redirect_auth
  Scenario: Do not follow redirects when Authorization header is present
    Given an outgoing request to "https://moltbook.com/api/v1/posts"
    And the request includes header "Authorization: Bearer <api_key>"
    And the server responds with a redirect to "https://www.moltbook.com/api/v1/posts"
    When the client receives the redirect response
    Then the client must not automatically retry with Authorization on the redirected host
    And the client must re-issue a fresh request directly to "https://www.moltbook.com/api/v1/posts"
    And a security event "REDIRECT_WITH_AUTH_DETECTED" is emitted

  @phase0 @log_safety
  Scenario: Never log raw API keys
    Given the system logs all HTTP requests and responses
    When a request is made with header "Authorization: Bearer moltbook_xxx"
    Then logs must redact the API key value
    And the log entry must include "Authorization: Bearer [REDACTED]"
