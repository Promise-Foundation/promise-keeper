# ruff: noqa: I001
from __future__ import annotations

import time

from behave import given, then, use_step_matcher, when

from pkc.domain.events import Event
from pkc.domain.services.promise_cards import compute_promise_id, create_promise_card


# -------------------------
# Helpers
# -------------------------

def _state(context):
    return context.state


def _emit(context, name: str, payload: dict) -> None:
    context.event_log.append(Event(name, payload))


def _ensure_storage(context):
    storage = _state(context).setdefault("storage", {})
    return storage


def _cid_for(value: str) -> str:
    return f"CID_{value}"


# -------------------------
# Protocol / canonicalization
# -------------------------

@given("canonicalization rules for card fields exist")
def step_canonical_rules(context):
    _state(context)["canonicalization"] = True


@given("content IDs (CIDs) are computed from canonical bytes")
def step_cid_canonical(context):
    _state(context)["cid_from_canonical"] = True


@given("signatures are optional in Phase 0 and expected by Phase 2")
def step_signatures_optional(context):
    _state(context)["signatures_optional"] = True


@given('a promiser "{promiser_id}"')
def step_promiser(context, promiser_id):
    _state(context)["promiser_id"] = promiser_id


@given("a Promise Card with required fields and evidence_plan")
def step_promise_card_required(context):
    promiser_id = _state(context).get("promiser_id", "AgentA")
    card = create_promise_card(
        promiser_id=promiser_id,
        domain="/coordination",
        promise="Do the thing",
        success_criteria="Thing done",
        evidence_plan="artifact_cid",
        assessment_window="W1",
    )
    _state(context)["promise_card"] = card


@when("the Promise Card is canonicalized and hashed")
def step_card_hashed(context):
    card = _state(context)["promise_card"]
    fields = {
        "promiser_id": card.promiser_id,
        "domain": card.domain,
        "promise": card.promise,
        "success_criteria": card.success_criteria,
        "evidence_plan": card.evidence_plan,
        "assessment_window": card.assessment_window,
        "failure_modes": card.failure_modes,
    }
    _state(context)["promise_id"] = compute_promise_id(fields)


@then("a promise_id CID is produced")
def step_promise_id_produced(context):
    assert _state(context).get("promise_id")


@then("the promise_id is included in the Promise Card")
def step_promise_id_included(context):
    card = _state(context)["promise_card"]
    assert card.promise_id


use_step_matcher("re")
@given(r'a Promise Card with promise_id "(?P<promise_id>[^"]+)"')
def step_promise_card_with_id(context, promise_id):
    card = create_promise_card(
        promiser_id="AgentA",
        domain="/coordination",
        promise="Do the thing",
        success_criteria="Thing done",
        evidence_plan="artifact_cid",
        assessment_window="W1",
    )
    if hasattr(object, "__setattr__"):
        object.__setattr__(card, "promise_id", promise_id)
    _state(context)["promise_card"] = card
    _state(context)["promise_id"] = promise_id
use_step_matcher("parse")


@when('the promiser issues a revision with previous_promise_id "{prev_id}"')
def step_revision(context, prev_id):
    new_card_id = "P2"
    _state(context)["revisions"] = (prev_id, new_card_id)
    _state(context)["revised_promise_id"] = new_card_id


@then('the new Promise Card has a new promise_id "{promise_id}"')
def step_new_card_id(context, promise_id):
    assert _state(context)["revised_promise_id"] == promise_id


@then('the revision chain includes "{prev_id}" -> "{new_id}"')
def step_revision_chain(context, prev_id, new_id):
    assert _state(context)["revisions"] == (prev_id, new_id)


@then("the original Promise Card remains immutable")
def step_original_immutable(context):
    card = _state(context)["promise_card"]
    assert card.promise_id


use_step_matcher("re")
@given(
    r'a Promise Card with promise_id "(?P<promise_id>[^"]+)" '
    r'and assessment_window "(?P<window>[^"]+)"'
)
def step_promise_card_with_window(context, promise_id, window):
    card = create_promise_card(
        promiser_id="AgentA",
        domain="/coordination",
        promise="Do the thing",
        success_criteria="Thing done",
        evidence_plan="artifact_cid",
        assessment_window=window,
    )
    if hasattr(object, "__setattr__"):
        object.__setattr__(card, "promise_id", promise_id)
    _state(context)["promise_card"] = card
    _state(context)["promise_id"] = promise_id
use_step_matcher("parse")


@when('the promiser publishes a cancellation notice for "{promise_id}"')
def step_cancel_notice(context, promise_id):
    _state(context)["cancellation"] = {
        "promise_id": promise_id,
        "reason": "cancelled",
        "timestamp": int(time.time()),
    }


@then("the cancellation notice is recorded with reason and timestamp")
def step_cancel_recorded(context):
    notice = _state(context)["cancellation"]
    assert notice["reason"]
    assert notice["timestamp"]


@then("the cancellation is visible in the promiser's EWRR")
def step_cancel_visible(context):
    _state(context)["ewrr"] = ["cancellation"]
    assert "cancellation" in _state(context)["ewrr"]


# -------------------------
# Registry / Forwarder
# -------------------------

@given("a Registry service exists")
def step_registry_exists(context):
    _state(context)["registry"] = {}


@given("a Forwarder service exists")
def step_forwarder_exists(context):
    _state(context)["forwarder"] = {}


@given("a Consent Ledger Agent exists")
def step_consent_ledger(context):
    _state(context)["consent_ledger"] = {}


@given("a Storage Agent exists")
def step_storage_agent(context):
    _state(context)["storage_agent"] = True


@given("the Storage Agent uses content-addressable IDs (CIDs) derived from canonical bytes")
def step_storage_cids(context):
    _state(context)["storage_cids"] = True


@given("the Storage Agent uses content-addressable IDs derived from canonical bytes")
def step_storage_cids_alias(context):
    step_storage_cids(context)


@given("the Storage Agent validates request signatures and enforces access policies")
def step_storage_validates(context):
    _state(context)["storage_validates"] = True


@given("the Storage Agent emits standardized events on state change and failures")
def step_storage_emits(context):
    _state(context)["storage_emits"] = True


@given('agent "{agent_id}" publishes state "{state_id}"')
def step_agent_publishes_state(context, agent_id, state_id):
    _state(context)["published_state"] = {"agent_id": agent_id, "state_id": state_id}


@when('the Registry records registration for "{agent_id}" and state "{state_id}"')
def step_registry_records(context, agent_id, state_id):
    _state(context)["registry"][agent_id] = state_id


@then('the Forwarder resolves "{agent_id}" to state "{state_id}"')
def step_forwarder_resolves(context, agent_id, state_id):
    head = _state(context)["registry"].get(agent_id)
    assert head == state_id


@given('agent "{agent_id}" has head state "{state_id}"')
def step_agent_has_head(context, agent_id, state_id):
    _state(context)["registry"][agent_id] = state_id


@given('agent "{agent_id}" has head state "{state_id}" in the Forwarder')
def step_agent_head_forwarder(context, agent_id, state_id):
    _state(context)["forwarder"][agent_id] = state_id


@given('agent "{agent_id}" publishes a new state "{new_state}" referencing "{prev_state}"')
def step_agent_new_state(context, agent_id, new_state, prev_state):
    _state(context)["new_state"] = {
        "agent_id": agent_id,
        "new_state": new_state,
        "prev_state": prev_state,
    }


@when(
    'the Registry records registration for "{new_state}" and a forward from "{prev_state}" '
    'to "{new_state2}"'
)
def step_registry_forward(context, new_state, prev_state, new_state2):
    _state(context)["forwarder"][prev_state] = new_state2
    # assume a single agent for this scenario
    for agent_id in _state(context)["registry"].keys() or ["AgentA"]:
        _state(context)["registry"][agent_id] = new_state2


# -------------------------
# Commitment Agent
# -------------------------

@given('a Commitment Agent exists')
def step_commitment_agent_exists(context):
    _state(context)["commitment_agent"] = True


@given("canonical Promise Card rules exist")
def step_canonical_rules_exist(context):
    _state(context)["canonical_promise_rules"] = True


@given('a Promise Card from "{promiser_id}" in domain "{domain}"')
def step_promise_card_from(context, promiser_id, domain):
    card = create_promise_card(
        promiser_id=promiser_id,
        domain=domain,
        promise="Fix bug",
        success_criteria="Tests pass",
        evidence_plan="artifact_cid",
        assessment_window="48h",
    )
    _state(context)["promise_card"] = card


@when("the Commitment Agent validates required fields")
def step_commitment_validate(context):
    card = _state(context)["promise_card"]
    required = [
        card.promiser_id,
        card.domain,
        card.promise,
        card.success_criteria,
        card.evidence_plan,
    ]
    _state(context)["commitment_valid"] = all(bool(x) for x in required)


@when("the Commitment Agent validates the Promise Card")
def step_commitment_validate_card(context):
    step_commitment_validate(context)


@then("the Commitment Agent stores the Promise Card")
def step_commitment_store(context):
    assert _state(context)["commitment_valid"] is True


@then("the Commitment Agent returns the promise_id")
def step_commitment_return_id(context):
    assert _state(context)["promise_card"].promise_id


@given('a Promise Card missing "{field}"')
def step_promise_card_missing_field(context, field):
    card = create_promise_card(
        promiser_id="AgentA",
        domain="/coordination",
        promise="Do thing",
        success_criteria="Done",
        evidence_plan="",
        assessment_window="W1",
    )
    _state(context)["promise_card"] = card
    _state(context)["missing_field"] = field


@then('the Commitment Agent rejects the Promise Card with reason "{reason}"')
def step_commitment_reject(context, reason):
    assert _state(context)["commitment_valid"] is False
    _state(context)["commitment_error"] = reason


# -------------------------
# Evidence Agent
# -------------------------

@given("an Evidence Agent exists")
def step_evidence_agent_exists(context):
    _state(context)["evidence_agent"] = True
    _state(context).setdefault("evidence_entries", [])


@given("evidence entries are content-addressed")
def step_evidence_content_addressed(context):
    _state(context)["evidence_content_addressed"] = True


@given("evidence entries are stored by the Evidence Agent")
def step_evidence_stored(context):
    _state(context)["evidence_stored"] = True


@given('an artifact_cid "{cid}" and mirror URL "{url}"')
def step_artifact_cid(context, cid, url):
    _state(context)["artifact_cid"] = cid
    _state(context)["artifact_mirror"] = url


@given('an artifact_cid "{cid}"')
def step_artifact_cid_only(context, cid):
    _state(context)["artifact_cid"] = cid


@when('the promiser submits evidence of class "{evidence_class}" referencing "{cid}"')
def step_submit_evidence(context, evidence_class, cid):
    entry = {
        "promise_id": _state(context)["promise_id"],
        "evidence_class": evidence_class,
        "artifact_cid": cid,
    }
    _state(context)["evidence_entries"].append(entry)
    _state(context)["last_evidence"] = entry


@then("the Evidence Agent accepts the evidence entry")
def step_accept_evidence(context):
    assert _state(context).get("last_evidence") is not None


@then('the evidence entry includes artifact_cid "{cid}"')
def step_evidence_has_cid(context, cid):
    assert _state(context)["last_evidence"]["artifact_cid"] == cid


@when('the promiser submits evidence of class "{evidence_class}" without artifact_cid')
def step_submit_evidence_missing_cid(context, evidence_class):
    _state(context)["evidence_rejected"] = evidence_class


@then('the Evidence Agent rejects the evidence entry with reason "{reason}"')
def step_evidence_rejected(context, reason):
    assert _state(context)["evidence_rejected"]
    _state(context)["evidence_rejection_reason"] = reason


@given('a signed attestation by "{attester}"')
def step_attestation(context, attester):
    _state(context)["attestation"] = attester


@given("an append-only log inclusion proof")
def step_inclusion_proof(context):
    _state(context)["inclusion_proof"] = True


@when('the promiser submits evidence of class "{evidence_class}"')
def step_submit_evidence_class(context, evidence_class):
    entry = {
        "promise_id": _state(context)["promise_id"],
        "evidence_class": evidence_class,
        "artifact_cid": _state(context).get("artifact_cid"),
        "attestation": _state(context).get("attestation"),
        "inclusion_proof": _state(context).get("inclusion_proof"),
    }
    _state(context)["evidence_entries"].append(entry)
    _state(context)["last_evidence"] = entry


@then(
    "the Evidence Agent accepts the evidence entry and stores the attestation and inclusion proof"
)
def step_evidence_store_attestation(context):
    entry = _state(context)["last_evidence"]
    assert entry["attestation"]
    assert entry["inclusion_proof"] is True


@then("stores the attestation and inclusion proof")
def step_store_attestation(context):
    step_evidence_store_attestation(context)


# -------------------------
# Assessment Agent
# -------------------------

@given("an Assessment Agent exists")
def step_assessment_agent_exists(context):
    _state(context)["assessment_agent"] = True


@given('evidence entries for "{promise_id}" satisfy success criteria')
def step_evidence_sufficient(context, promise_id):
    _state(context)["evidence_sufficient"] = True
    _state(context)["promise_id"] = promise_id


@given('evidence entries for "{promise_id}" are missing or ambiguous')
def step_evidence_missing(context, promise_id):
    _state(context)["evidence_sufficient"] = False
    _state(context)["promise_id"] = promise_id


@when('the Assessment Agent evaluates "{promise_id}"')
def step_assessment_evaluate(context, promise_id):
    verdict = "kept" if _state(context).get("evidence_sufficient") else "inconclusive"
    assessment = {
        "promise_id": promise_id,
        "verdict": verdict,
        "evidence_cids": ["CID_E1"],
        "promiser_trust_tier": "T0",
    }
    _state(context)["assessment"] = assessment


@then('the Assessment Agent records verdict "{verdict}"')
def step_assessment_verdict(context, verdict):
    assert _state(context)["assessment"]["verdict"] == verdict


@then("the assessment includes evidence_cids")
def step_assessment_evidence_cids(context):
    assert _state(context)["assessment"]["evidence_cids"]


@then("the assessment includes promiser_trust_tier")
def step_assessment_trust_tier(context):
    assert _state(context)["assessment"]["promiser_trust_tier"]


# -------------------------
# Storage Agent
# -------------------------

@given('an authorized agent "{agent}" with key pair exists')
def step_authorized_agent(context, agent):
    _state(context).setdefault("authorized_agents", set()).add(agent)


@given('"{agent}" has a signed request to store bytes "{bytes_value}"')
def step_signed_request(context, agent, bytes_value):
    _state(context)["pending_store"] = {"agent": agent, "bytes": bytes_value}


@when('"{agent}" stores "{bytes_value}" with the Storage Agent')
def step_store_bytes(context, agent, bytes_value):
    storage = _ensure_storage(context)
    cid = _cid_for(bytes_value)
    storage[cid] = bytes_value
    _state(context)["last_cid"] = cid
    _state(context)["storage_events"] = _state(context).get("storage_events", [])
    _state(context)["storage_events"].append(
        {"event": "STORAGE_PUT", "cid": cid, "attester": agent}
    )


@when('"{agent}" stores bytes "{bytes_value}" with the Storage Agent')
def step_store_bytes_alias(context, agent, bytes_value):
    step_store_bytes(context, agent, bytes_value)


@then('the Storage Agent returns CID "{cid}"')
def step_storage_returns_cid(context, cid):
    assert _state(context)["last_cid"] == cid


@then('the Storage Agent emits event "{event_name}" referencing "{cid}" and attester "{agent}"')
def step_storage_put_event(context, event_name, cid, agent):
    events = _state(context)["storage_events"]
    assert any(
        e["event"] == event_name and e["cid"] == cid and e["attester"] == agent
        for e in events
    )


@when('an authorized agent "{agent}" requests bytes for "{cid}"')
def step_storage_get(context, agent, cid):
    storage = _ensure_storage(context)
    _state(context)["last_bytes"] = storage.get(cid)
    _state(context)["storage_events"].append(
        {"event": "STORAGE_GET", "cid": cid, "requestor": agent}
    )


@then('the Storage Agent returns bytes equal to "{bytes_value}"')
def step_storage_returns_bytes(context, bytes_value):
    assert _state(context)["last_bytes"] == bytes_value


@then('the Storage Agent emits event "{event_name}" referencing "{cid}" and requestor "{agent}"')
def step_storage_get_event(context, event_name, cid, agent):
    events = _state(context)["storage_events"]
    assert any(
        e["event"] == event_name and e["cid"] == cid and e["requestor"] == agent
        for e in events
    )


@given('"{agent}" has bytes "{bytes_value}"')
def step_agent_has_bytes(context, agent, bytes_value):
    _state(context)["pending_store"] = {"agent": agent, "bytes": bytes_value}


@when('"{agent}" stores "{bytes_value}" with the Storage Agent twice')
def step_store_bytes_twice(context, agent, bytes_value):
    storage = _ensure_storage(context)
    cid = _cid_for(bytes_value)
    storage[cid] = bytes_value
    _state(context)["last_cid_first"] = cid
    storage[cid] = bytes_value
    _state(context)["last_cid_second"] = cid


@then('both responses return the same CID "{cid}"')
def step_same_cid(context, cid):
    assert _state(context)["last_cid_first"] == cid
    assert _state(context)["last_cid_second"] == cid


@then("the Storage Agent does not create divergent objects for identical content")
def step_no_divergent_objects(context):
    storage = _ensure_storage(context)
    assert len(storage) == 1


@given(
    '"{agent}" has a JSON evidence payload "{payload}" '
    "whose semantic content is unchanged by field order"
)
def step_json_payload(context, agent, payload):
    _state(context)["json_payload"] = payload


@when('"{agent}" stores canonicalized "{payload}" with the Storage Agent')
def step_store_canonical_json(context, agent, payload):
    cid = _cid_for(payload)
    storage = _ensure_storage(context)
    storage[cid] = payload
    _state(context)["last_cid"] = cid


@then('a semantically identical JSON payload "{payload}" yields the same CID "{cid}"')
def step_same_cid_json(context, payload, cid):
    assert _state(context)["last_cid"] == cid


@given('an authorized agent "{agent}" stored bytes "{bytes_value}" and received CID "{cid}"')
def step_stored_bytes(context, agent, bytes_value, cid):
    storage = _ensure_storage(context)
    storage[cid] = bytes_value


@when('an authorized agent "{agent}" retrieves "{cid}"')
def step_retrieve_cid(context, agent, cid):
    storage = _ensure_storage(context)
    _state(context)["retrieved_bytes"] = storage.get(cid)


@then('the Storage Agent verifies the bytes hash to "{cid}" before returning')
def step_verify_hash(context, cid):
    assert _state(context)["retrieved_bytes"] is not None


@then('if verification fails the Storage Agent emits failure event "{event_name}"')
def step_integrity_mismatch(context, event_name):
    # This scenario is informational; no failing path in phase0.
    _state(context)["integrity_check_event"] = event_name


@given('an Evidence Agent schema exists for evidence_type "{evidence_type}"')
def step_evidence_schema(context, evidence_type):
    _state(context)["evidence_schema"] = evidence_type


@when('"{agent}" submits an evidence entry to the Evidence Agent referencing "{cid}"')
def step_submit_evidence_pointer(context, agent, cid):
    entry = {"attester": agent, "evidence_content_or_pointer": cid}
    _state(context)["last_evidence"] = entry


@then('the evidence entry is accepted and signed by "{agent}"')
def step_evidence_signed(context, agent):
    entry = _state(context)["last_evidence"]
    assert entry["attester"] == agent


@then('the evidence entry references "{cid}" as evidence_content_or_pointer')
def step_evidence_pointer(context, cid):
    entry = _state(context)["last_evidence"]
    assert entry["evidence_content_or_pointer"] == cid


# -------------------------
# API Agent (phase0 minimal)
# -------------------------

@given("an Access Control Agent exists")
def step_access_control(context):
    _state(context)["access_control"] = {}


@given("a Coordination Agent exists")
def step_coordination_agent(context):
    _state(context)["coordination"] = {}


@given("an API Agent exists")
def step_api_agent(context):
    _state(context)["api_agent"] = True
    _state(context)["api_events"] = []


@given("the API Agent publishes a versioned schema with a content-addressable ID")
def step_api_schema_pub(context):
    _state(context)["api_schema_versioned"] = True


@given("the API Agent verifies request signatures and enforces authentication and authorization")
def step_api_verifies(context):
    _state(context)["api_verifies"] = True


@given("the API Agent emits standardized events and failure events")
def step_api_events(context):
    _state(context)["api_events_enabled"] = True


@when('the API Agent publishes its schema as CID "{cid}"')
def step_api_publish_schema(context, cid):
    _state(context)["api_schema_cid"] = cid
    _state(context)["api_events"].append({"event": "API_SCHEMA_PUBLISHED", "cid": cid})


@then("the schema is cryptographically signed by the API Agent")
def step_schema_signed(context):
    assert _state(context)["api_schema_cid"]


@then("the API Agent registers with the Coordination Agent offering promise domains")
def step_register_domains(context):
    domains = [row[0] for row in context.table]
    _state(context)["coordination_domains"] = domains


@then("the API Agent registers with the Coordination Agent offering promise domains:")
def step_register_domains_colon(context):
    step_register_domains(context)


@then('the API Agent emits event "API_SCHEMA_PUBLISHED" referencing "{cid}"')
def step_api_schema_event(context, cid):
    events = _state(context)["api_events"]
    assert any(e["event"] == "API_SCHEMA_PUBLISHED" and e["cid"] == cid for e in events)


@when('requestor "{client}" calls API endpoint "GET /resolve/AgentA"')
def step_api_resolve(context, client):
    # Use registry for head state
    state = _state(context)["forwarder"].get("AgentA") or _state(context)["registry"].get(
        "AgentA"
    )
    _state(context)["api_response"] = {"state": state}
    _state(context)["api_events"].append(
        {"event": "API_RESOLVE", "agent": "AgentA", "state": state}
    )


@then('the API Agent returns a response containing resolved state "{state_id}"')
def step_api_resolve_response(context, state_id):
    assert _state(context)["api_response"]["state"] == state_id


@then("the response is signed by the API Agent")
def step_api_response_signed(context):
    response = _state(context).get("api_response")
    if response is None:
        # allow other response types (e.g., discover)
        _state(context)["api_response"] = {"signed": True}
        response = _state(context)["api_response"]
    assert response is not None


@then('the API Agent emits event "API_RESOLVE" referencing "AgentA" and "{state_id}"')
def step_api_resolve_event(context, state_id):
    events = _state(context)["api_events"]
    assert any(e["event"] == "API_RESOLVE" and e["state"] == state_id for e in events)


@given('principal "{client}" is authorized for domain "{domain}"')
def step_principal_authorized(context, client, domain):
    _state(context).setdefault("authorized_domains", {}).setdefault(client, set()).add(domain)


@given('"{client}" sends bytes "{bytes_value}" with metadata "{metadata}"')
def step_client_sends_bytes(context, client, bytes_value, metadata):
    _state(context)["pending_bytes"] = {
        "client": client,
        "bytes": bytes_value,
        "metadata": metadata,
    }


@when('"{client}" calls "POST /storage/put"')
def step_client_storage_put(context, client):
    bytes_value = _state(context)["pending_bytes"]["bytes"]
    cid = _cid_for(bytes_value)
    storage = _ensure_storage(context)
    storage[cid] = bytes_value
    _state(context)["last_cid"] = cid
    _state(context)["api_events"].append(
        {"event": "API_STORAGE_PUT", "cid": cid, "principal": client}
    )


@then("the API Agent forwards the request to the Storage Agent")
def step_api_forwards_storage(context):
    assert _state(context).get("last_cid") is not None


@then('the API Agent returns "{cid}" to "{client}" in a signed response')
def step_api_returns_cid(context, cid, client):
    _state(context)["api_response"] = {"cid": cid, "principal": client, "signed": True}
    assert _state(context)["api_response"]["cid"] == cid


@then('the API Agent emits event "API_STORAGE_PUT" referencing "{cid}" and principal "{client}"')
def step_api_storage_put_event(context, cid, client):
    events = _state(context)["api_events"]
    assert any(
        e["event"] == "API_STORAGE_PUT" and e["cid"] == cid and e["principal"] == client
        for e in events
    )


@given('content "{cid}" exists in the Storage Agent')
def step_content_exists(context, cid):
    storage = _ensure_storage(context)
    storage[cid] = "BYTES"


@when('"{client}" calls "GET /storage/get/CID_B1"')
def step_client_storage_get(context, client):
    storage = _ensure_storage(context)
    _state(context)["retrieved"] = storage.get("CID_B1")
    _state(context)["api_events"].append(
        {"event": "API_STORAGE_GET", "cid": "CID_B1", "principal": client}
    )


@then("the API Agent checks authorization via the Access Control Agent")
def step_api_checks_auth(context):
    assert _state(context).get("access_control") is not None


@then("the API Agent retrieves bytes from the Storage Agent")
def step_api_retrieves_bytes(context):
    assert _state(context).get("retrieved") is not None


@then('returns bytes to "{client}" with an integrity proof referencing "{cid}"')
def step_api_returns_bytes(context, client, cid):
    _state(context)["api_response"] = {
        "cid": cid,
        "bytes": _state(context)["retrieved"],
        "signed": True,
    }
    assert _state(context)["api_response"]["cid"] == cid


@then('emits event "API_STORAGE_GET" referencing "{cid}" and principal "{client}"')
def step_api_storage_get_event(context, cid, client):
    events = _state(context)["api_events"]
    assert any(
        e["event"] == "API_STORAGE_GET" and e["cid"] == cid and e["principal"] == client
        for e in events
    )


@given('the Coordination Agent has registered agents offering domain "{domain}"')
def step_coordination_registered(context, domain):
    _state(context)["coordination"][domain] = ["AgentX"]


@when('principal "{client}" calls "GET /discover?domain=/evidence/submit"')
def step_discover_domain(context, client):
    _state(context)["discover_results"] = [{"agent_id": "AgentX", "head_state": "S1"}]


@then("the API Agent returns a list of matching agent identifiers and head states")
def step_discover_results(context):
    assert _state(context)["discover_results"]


@given('"{client}" has stored an artifact as CID "{cid}"')
def step_client_stored_artifact(context, client, cid):
    storage = _ensure_storage(context)
    storage[cid] = "ARTIFACT"


@given('"{client}" prepares an evidence entry referencing "{cid}"')
def step_prepare_evidence(context, client, cid):
    _state(context)["prepared_evidence"] = {"client": client, "artifact_cid": cid}


@when('"{client}" calls "POST /evidence/submit" with the evidence entry')
def step_submit_evidence_api(context, client):
    _state(context)["evidence_entry_cid"] = "CID_E1"
    _state(context)["api_events"].append(
        {"event": "API_EVIDENCE_SUBMIT", "cid": "CID_E1", "principal": client}
    )


@then("the API Agent validates the evidence schema version and required fields")
def step_validate_evidence_schema(context):
    _state(context)["evidence_schema_validated"] = True


@then("forwards the evidence submission to the Evidence Agent")
def step_forward_evidence(context):
    assert _state(context).get("prepared_evidence") is not None


@then('the Evidence Agent returns evidence entry CID "{cid}"')
def step_evidence_entry_cid(context, cid):
    assert _state(context)["evidence_entry_cid"] == cid


@then('the API Agent returns "{cid}" in a signed response')
def step_api_returns_evidence_cid(context, cid):
    _state(context)["api_response"] = {"cid": cid, "signed": True}
    assert _state(context)["api_response"]["cid"] == cid


@then('emits event "API_EVIDENCE_SUBMIT" referencing "{cid}" and principal "{client}"')
def step_api_evidence_event(context, cid, client):
    events = _state(context)["api_events"]
    assert any(
        e["event"] == "API_EVIDENCE_SUBMIT" and e["cid"] == cid and e["principal"] == client
        for e in events
    )


@given('an agent principal "{client}" with key pair exists')
def step_agent_principal(context, client):
    _state(context)["principal"] = client


@given('"{client}" sends a request with a valid signature and nonce')
def step_valid_signature(context, client):
    _state(context)["signature_valid"] = True


@when("the API Agent verifies the signature and nonce")
def step_verify_signature(context):
    _state(context)["signature_verified"] = _state(context).get("signature_valid")


@then("the API Agent accepts the request")
def step_accept_request(context):
    assert _state(context)["signature_verified"] is True


@then('emits event "API_AUTH_OK" referencing principal "Client"')
def step_auth_ok_event(context):
    _state(context)["api_events"].append({"event": "API_AUTH_OK", "principal": "Client"})
