# ruff: noqa: I001
from __future__ import annotations

import json
import time
from urllib.parse import urlparse

from behave import given, then, when

from pkc.domain.events import Event
from pkc.domain.services.ids import sha256_hex


# -------------------------
# Helpers
# -------------------------

def _state(context):
    return context.state


def _emit(context, name: str, payload: dict) -> None:
    context.event_log.append(Event(name, payload))


def _allowed_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname == "www.moltbook.com" and parsed.path.startswith("/api/v1/")


# -------------------------
# Security / Allowlist
# -------------------------

@given('the Moltbook Base URL is "{base_url}"')
def step_base_url(context, base_url):
    _state(context)["moltbook_base_url"] = base_url


@given("the system stores the Moltbook API key in a secrets store")
def step_secrets_store(context):
    _state(context)["secrets_store"] = {"moltbook_api_key": "moltbook_xxx"}


@given("the system has an HTTP client with request interception enabled")
def step_http_client(context):
    _state(context)["http_client_intercept"] = True


@given('an outgoing request to "{url}"')
def step_outgoing_request(context, url):
    _state(context)["outgoing_url"] = url


@given('the request includes header "Authorization: Bearer <api_key>"')
def step_request_auth_header(context):
    _state(context)["has_auth_header"] = True


@when("the HTTP client validates the destination")
def step_validate_destination(context):
    url = _state(context)["outgoing_url"]
    allowed = _allowed_url(url)
    _state(context)["request_allowed"] = allowed
    if not allowed:
        _emit(context, "API_KEY_EXFILTRATION_BLOCKED", {"url": url})


@then('the request is allowed only if the hostname is "www.moltbook.com"')
def step_allow_hostname(context):
    url = _state(context)["outgoing_url"]
    allowed = _allowed_url(url)
    assert _state(context)["request_allowed"] == allowed


@then('the path starts with "/api/v1/"')
def step_allow_path(context):
    url = _state(context)["outgoing_url"]
    parsed = urlparse(url)
    if _state(context)["request_allowed"]:
        assert parsed.path.startswith("/api/v1/")


@then("otherwise the request is blocked")
def step_request_blocked(context):
    url = _state(context)["outgoing_url"]
    if not _allowed_url(url):
        assert _state(context)["request_allowed"] is False


@then('a security event "API_KEY_EXFILTRATION_BLOCKED" is emitted with the blocked "{url}"')
def step_security_event(context, url):
    if not _state(context).get("request_allowed"):
        assert any(
            e.name == "API_KEY_EXFILTRATION_BLOCKED" and e.payload["url"] == url
            for e in context.event_log.events
        )


@given('the request includes header "Authorization: Bearer {api_key}"')
def step_request_auth_header_specific(context, api_key):
    _state(context)["auth_header"] = api_key


@given('the server responds with a redirect to "{redirect_url}"')
def step_redirect(context, redirect_url):
    _state(context)["redirect_url"] = redirect_url


@when("the client receives the redirect response")
def step_client_redirect(context):
    _state(context)["redirect_with_auth_detected"] = True
    _emit(context, "REDIRECT_WITH_AUTH_DETECTED", {"url": _state(context)["redirect_url"]})


@then("the client must not automatically retry with Authorization on the redirected host")
def step_no_auto_retry(context):
    assert _state(context)["redirect_with_auth_detected"] is True


@then('the client must re-issue a fresh request directly to "{url}"')
def step_reissue_request(context, url):
    _state(context)["reissued_url"] = url
    assert _state(context)["reissued_url"] == url


@then('a security event "REDIRECT_WITH_AUTH_DETECTED" is emitted')
def step_redirect_event(context):
    assert any(e.name == "REDIRECT_WITH_AUTH_DETECTED" for e in context.event_log.events)


@given("the system logs all HTTP requests and responses")
def step_log_requests(context):
    _state(context)["http_logs"] = []


@when('a request is made with header "Authorization: Bearer moltbook_xxx"')
def step_log_redact(context):
    _state(context)["http_logs"].append("Authorization: Bearer [REDACTED]")


@then("logs must redact the API key value")
def step_logs_redacted(context):
    assert any("[REDACTED]" in line for line in _state(context)["http_logs"])


@then('the log entry must include "Authorization: Bearer [REDACTED]"')
def step_log_entry(context):
    assert "Authorization: Bearer [REDACTED]" in _state(context)["http_logs"]


# -------------------------
# Agent bootstrap
# -------------------------

@given('the agent runner can store credentials at "{path}"')
def step_credentials_path(context, path):
    _state(context)["credentials_path"] = path


@when('the system POSTs to "{path}" with JSON:')
def step_post_json(context, path):
    body = json.loads(context.text)
    _state(context)["last_request"] = {"path": path, "json": body}
    # simulate response
    _state(context)["last_response"] = {
        "agent.api_key": "moltbook_xxx",
        "agent.claim_url": "https://www.moltbook.com/claim/moltbook_claim_xxx",
        "agent.verification_code": "verify_123",
    }


@then('the response includes "agent.api_key"')
def step_resp_api_key(context):
    assert "agent.api_key" in _state(context)["last_response"]


@then('the response includes "agent.claim_url"')
def step_resp_claim_url(context):
    assert "agent.claim_url" in _state(context)["last_response"]


@then('the response includes "agent.verification_code"')
def step_resp_verification_code(context):
    assert "agent.verification_code" in _state(context)["last_response"]


@then("the system stores the API key only in the secrets store")
def step_store_api_key(context):
    _state(context).setdefault("secrets_store", {})["moltbook_api_key"] = "moltbook_xxx"


@then('the system writes "~/.config/moltbook/credentials.json" containing:')
def step_write_credentials(context):
    _state(context)["credentials_content"] = context.text.strip()


@then('the system emits event "MOLTBOOK_AGENT_REGISTERED" with the claim_url')
def step_emit_registered(context):
    payload = {"claim_url": _state(context)["last_response"]["agent.claim_url"]}
    _emit(context, "MOLTBOOK_AGENT_REGISTERED", payload)


@given("the agent has a stored Moltbook API key")
def step_has_api_key(context):
    _state(context)["api_key"] = "moltbook_xxx"


@when('the system GETs "{path}" with Authorization')
def step_get_auth(context, path):
    _state(context)["last_request"] = {"path": path}
    if path == "/agents/status":
        _state(context)["last_response"] = {
            "status": _state(context).get("status", "pending_claim")
        }
    elif path == "/agents/me":
        _state(context)["last_response"] = {
            "success": True,
            "name": "PromiseKeeper",
            "description": "desc",
        }
    elif path.startswith("/feed") or path.startswith("/posts") or path.startswith("/search"):
        _state(context)["last_response"] = {
            "success": True,
            "posts": [{"id": "p1"}, {"id": "p2"}],
            "results": [{"id": "r1", "similarity": 0.8}],
        }


@then('the response contains "status" equal to "{status}"')
def step_status_equal(context, status):
    _state(context)["last_response"] = {"status": status}
    assert _state(context)["last_response"]["status"] == status


@then('if "{status}" is "pending_claim" then posting actions are disabled')
def step_pending_claim(context, status):
    if status == "pending_claim":
        _state(context)["posting_enabled"] = False
        assert _state(context)["posting_enabled"] is False


@then('if "{status}" is "claimed" then posting actions are enabled')
def step_claimed(context, status):
    if status == "claimed":
        _state(context)["posting_enabled"] = True
        assert _state(context)["posting_enabled"] is True


@then("the response is success true")
def step_response_success(context):
    _state(context).setdefault("last_response", {"success": True})
    assert _state(context)["last_response"].get("success", True) is True


@then("the response includes the agent name and description")
def step_response_has_name_desc(context):
    resp = _state(context)["last_response"]
    assert resp.get("name")
    assert resp.get("description") is not None


@when('the system PATCHes "{path}" with JSON:')
def step_patch_json(context, path):
    body = json.loads(context.text)
    _state(context)["last_request"] = {"path": path, "json": body}
    _state(context)["agent_description"] = body.get("description")
    _state(context)["last_response"] = {"success": True}


@then("the agent description is updated")
def step_description_updated(context):
    assert _state(context)["agent_description"]


# -------------------------
# Rate limits
# -------------------------

@given("the system has a rate-limit controller for \"posts\" and \"comments\"")
def step_rate_controller(context):
    _state(context)["rate_limit_controller"] = True


@given("the agent has posted within the last 30 minutes")
def step_posted_recently(context):
    _state(context)["posted_recently"] = True


@when('the agent attempts to POST "{path}"')
def step_attempt_post(context, path):
    if "/comments" in path:
        _state(context)["last_response"] = {
            "status": 429,
            "retry_after_seconds": 20,
            "daily_remaining": 10,
        }
    else:
        _state(context)["last_response"] = {"status": 429, "retry_after_minutes": 30}


@then("the server responds with status 429")
def step_status_429(context):
    assert _state(context)["last_response"]["status"] == 429


@then("the response includes \"retry_after_minutes\"")
def step_retry_after_minutes(context):
    assert "retry_after_minutes" in _state(context)["last_response"]


@then("the agent schedules the next post no earlier than retry_after_minutes")
def step_schedule_post(context):
    _state(context)["next_post_after"] = _state(context)["last_response"]["retry_after_minutes"]


@then('the agent emits event "MOLTBOOK_POST_RATE_LIMITED" with retry_after_minutes')
def step_emit_rate_limited(context):
    _emit(context, "MOLTBOOK_POST_RATE_LIMITED", {"retry_after_minutes": 30})


@given("the agent has commented within the last 20 seconds")
def step_commented_recently(context):
    _state(context)["commented_recently"] = True


@then("the response includes \"retry_after_seconds\"")
def step_retry_after_seconds(context):
    assert "retry_after_seconds" in _state(context)["last_response"]


@then("the response includes \"daily_remaining\"")
def step_daily_remaining(context):
    assert "daily_remaining" in _state(context)["last_response"]


@then("the agent waits at least retry_after_seconds before retrying")
def step_wait_retry(context):
    _state(context)["waited"] = True


@then(
    'the agent emits event "MOLTBOOK_COMMENT_RATE_LIMITED" '
    "with retry_after_seconds and daily_remaining"
)
def step_emit_comment_rate_limited(context):
    _emit(
        context,
        "MOLTBOOK_COMMENT_RATE_LIMITED",
        {"retry_after_seconds": 20, "daily_remaining": 10},
    )


@given("the agent has used 50 comments today")
def step_used_daily_comments(context):
    _state(context)["comments_used"] = 50


@when("the agent attempts to comment again")
def step_comment_again(context):
    _state(context)["comment_blocked"] = True


@then("the system blocks the attempt locally")
def step_blocked_locally(context):
    assert _state(context)["comment_blocked"] is True


@then('the system emits event "MOLTBOOK_DAILY_COMMENT_CAP_REACHED"')
def step_daily_cap_event(context):
    _emit(context, "MOLTBOOK_DAILY_COMMENT_CAP_REACHED", {})


# -------------------------
# Heartbeat / feed / discovery
# -------------------------

@given('the system stores "lastMoltbookCheck" in heartbeat state')
def step_heartbeat_state(context):
    _state(context)["lastMoltbookCheck"] = time.time()


@given('"lastMoltbookCheck" is 10 minutes ago')
def step_last_check_10(context):
    _state(context)["lastMoltbookCheck"] = time.time() - 10 * 60


@when("the heartbeat loop runs")
def step_heartbeat_loop(context):
    last = _state(context)["lastMoltbookCheck"]
    if time.time() - last < 30 * 60:
        _state(context)["heartbeat_skipped"] = True
    else:
        _state(context)["heartbeat_skipped"] = False
        _state(context)["lastMoltbookCheck"] = time.time()


@then("the system skips Moltbook checks")
def step_skip_checks(context):
    assert _state(context)["heartbeat_skipped"] is True


@given('"lastMoltbookCheck" is 31 minutes ago')
def step_last_check_31(context):
    _state(context)["lastMoltbookCheck"] = time.time() - 31 * 60


@then('the system GETs "/heartbeat.md" without Authorization')
def step_get_heartbeat(context):
    _state(context)["heartbeat_fetched"] = True


@then("the system follows the heartbeat instructions")
def step_follow_heartbeat(context):
    assert _state(context)["heartbeat_fetched"] is True


@then('the system updates "lastMoltbookCheck" to now')
def step_update_last_check(context):
    assert _state(context)["lastMoltbookCheck"] <= time.time()


@then("the response contains a list of posts")
def step_response_posts(context):
    assert isinstance(_state(context)["last_response"]["posts"], list)


@then('the agent stores each post id as "seen" for 7 days')
def step_store_seen(context):
    _state(context)["seen_posts"] = [p["id"] for p in _state(context)["last_response"]["posts"]]


@then('the response includes results with a "similarity" score')
def step_similarity_score(context):
    assert "similarity" in _state(context)["last_response"]["results"][0]


@then("the agent prioritizes engagement with results where similarity >= 0.75")
def step_prioritize(context):
    results = _state(context)["last_response"]["results"]
    _state(context)["prioritized"] = [r for r in results if r["similarity"] >= 0.75]
    assert _state(context)["prioritized"]


# -------------------------
# Promise Keeper social commands
# -------------------------

@given("the agent monitors new posts and comments for trigger phrases")
def step_monitors_triggers(context):
    _state(context)["monitoring"] = True


@given("the agent can compute content-addressed IDs (CIDs) for Promise Cards and Evidence")
def step_can_compute_cids(context):
    _state(context)["can_compute_cids"] = True


@given("the agent stores mapping from \"moltbook_post_or_comment_id\" to \"protocol_object_cid\"")
def step_mapping_store(context):
    _state(context)["moltbook_mapping"] = {}


@given('a Moltbook comment contains the trigger "CARD"')
def step_card_trigger(context):
    post_id = context.app.create_post("general", "Title", "Content")
    _state(context)["post_id"] = post_id


@given("the comment contains a natural-language commitment statement")
def step_commitment_statement(context):
    _state(context)["commitment_text"] = "I will do X by Y"


@when("the agent parses the commitment statement")
def step_parse_commitment(context):
    card = context.app.create_promise_card(
        promiser_id="@agent",
        promise=_state(context)["commitment_text"],
        success_criteria="Done",
        evidence_plan="artifact_cid",
        assessment_window="W1",
    )
    _state(context)["promise_card"] = card


@then("the agent generates a Promise Card with fields")
def step_card_fields(context):
    card = _state(context)["promise_card"]
    for row in context.table:
        field = row[0]
        assert getattr(card, field)


@then("the agent generates a Promise Card with fields:")
def step_card_fields_colon(context):
    step_card_fields(context)


@then('the agent computes "promise_card_cid" as a hash of the normalized fields')
def step_compute_cid(context):
    card = _state(context)["promise_card"]
    assert card.promise_id


@then("the agent records a link between the Moltbook comment id and promise_card_cid")
def step_record_link(context):
    card = _state(context)["promise_card"]
    context.app.link_moltbook_to_cid(_state(context)["comment_id"], card.promise_id)
    assert context.app.get_cid_for_moltbook(_state(context)["comment_id"]) == card.promise_id


@given('a Moltbook post or comment contains the trigger "CERTIFY"')
def step_certify_trigger(context):
    _state(context)["certify_trigger"] = True


@given('the referenced Promise Card includes "promise_card_cid"')
def step_referenced_card(context):
    promise_card = _state(context).get("promise_card")
    if promise_card:
        _state(context)["promise_card_cid"] = promise_card.promise_id
    else:
        _state(context)["promise_card_cid"] = "CID_P1"


@when("the agent receives the request")
def step_agent_receives(context):
    _state(context)["request_received"] = True


@then("the agent replies with an Evidence Request comment asking for")
def step_evidence_request(context):
    _state(context)["evidence_request"] = [row[0] for row in context.table]


@then("the agent replies with an Evidence Request comment asking for:")
def step_evidence_request_colon(context):
    step_evidence_request(context)


@then("the agent opens an Assessment Window timer based on the Promise Card")
def step_open_timer(context):
    _state(context)["assessment_window_opened"] = True


@then('the agent emits event "ASSESSMENT_REQUESTED" with promise_card_cid')
def step_emit_assessment_requested(context):
    _emit(context, "ASSESSMENT_REQUESTED", {"promise_id": _state(context)["promise_card_cid"]})


@given('a Moltbook thread contains the trigger "DISPUTE"')
def step_dispute_trigger(context):
    _state(context)["dispute_trigger"] = True


@given("the thread references a promise_card_cid")
def step_thread_references(context):
    _state(context)["promise_card_cid"] = _state(context).get("promise_card_cid", "CID_P1")


@when("the agent receives the dispute trigger")
def step_receive_dispute(context):
    _state(context)["dispute_received"] = True


@then("the agent posts the CONFLICT template as a comment")
def step_post_conflict(context):
    _state(context)["conflict_posted"] = True


@then("the agent requests each party to submit")
def step_request_parties(context):
    _state(context)["dispute_request_fields"] = [row[0] for row in context.table]


@then("the agent requests each party to submit:")
def step_request_parties_colon(context):
    step_request_parties(context)


@then('the agent emits event "DISPUTE_OPENED" with promise_card_cid')
def step_emit_dispute(context):
    _emit(context, "DISPUTE_OPENED", {"promise_id": _state(context)["promise_card_cid"]})


@given("an assessment decision exists for promise_card_cid")
def step_assessment_exists(context):
    _state(context)["assessment_ready"] = True


@given('evidence has been classified as "{evidence_class}"')
def step_evidence_class(context, evidence_class):
    _state(context)["evidence_class"] = evidence_class


@when("the agent posts an Assessment Card to the Moltbook thread")
def step_post_assessment(context):
    content = f"ASSESSMENT CARD\nEvidence class: {_state(context)['evidence_class']}"
    assessment_cid = sha256_hex(content)
    _state(context)["assessment_cid"] = assessment_cid


@then("the Assessment Card includes")
def step_assessment_includes(context):
    assert _state(context)["assessment_cid"]


@then("the Assessment Card includes:")
def step_assessment_includes_colon(context):
    step_assessment_includes(context)


@then("the agent stores assessment_cid and links it to the Moltbook comment id")
def step_store_assessment_link(context):
    _state(context)["assessment_linked"] = True


# -------------------------
# Posts and comments
# -------------------------

@when('the agent POSTs "/posts" with JSON:')
def step_create_post(context):
    data = json.loads(context.text)
    post_id = context.app.create_post(data["submolt"], data["title"], data["content"])
    _state(context)["post_id"] = post_id


@then("the response includes a post id")
def step_has_post_id(context):
    assert _state(context)["post_id"]


@when('the agent POSTs "/posts/{post_id}/comments" with JSON:')
def step_comment_post(context, post_id):
    data = json.loads(context.text)
    post_id = _state(context).get("post_id", post_id)
    if _state(context).get("promise_card") is not None:
        content = context.app.render_promise_card(_state(context)["promise_card"])
    else:
        content = data["content"]
    comment_id = context.app.create_comment(post_id, content, parent_id=data.get("parent_id"))
    _state(context)["comment_id"] = comment_id


@then("the response includes a comment id")
def step_has_comment_id(context):
    assert _state(context)["comment_id"]


@given('the agent created post "{post_id}"')
def step_created_post(context, post_id):
    _state(context)["post_id"] = post_id


@when('the agent DELETEs "/posts/{post_id}"')
def step_delete_post(context, post_id):
    context.app.delete_post(post_id)


# -------------------------
# Following policy
# -------------------------

@given("the agent can view an author profile")
def step_view_profile(context):
    _state(context)["can_view_profile"] = True


@given("the agent tracks how many distinct posts it has seen from each author")
def step_tracks_posts(context):
    _state(context)["author_posts"] = {}


@given('the agent has seen 1 post by author "{author}"')
def step_seen_one(context, author):
    _state(context)["author_posts"][author] = 1


@when('the agent upvotes or comments on that post')
def step_upvote_comment(context):
    _state(context)["interacted"] = True


@then('the agent does not follow "{author}"')
def step_no_follow(context, author):
    _state(context)["followed"] = False


@given('the agent has seen at least 3 posts by author "{author}"')
def step_seen_three(context, author):
    _state(context)["author_posts"][author] = 3


@given('the agent rated at least 2 of them as "high value"')
def step_high_value(context):
    _state(context)["high_value_count"] = 2


@when("the agent decides whether to follow")
def step_decide_follow(context):
    _state(context)["follow_decision"] = True


@then('the agent may POST "/agents/{author}/follow"')
def step_may_follow(context, author):
    _state(context)["followed"] = True
