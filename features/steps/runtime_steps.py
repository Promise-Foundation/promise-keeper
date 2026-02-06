from __future__ import annotations

import time

from behave import given, then, when

from pkc.runtime.heartbeat import run_heartbeat


def _state(context):
    return context.state


@given("the runtime heartbeat interval is 30 minutes")
def step_runtime_interval(context):
    _state(context)["heartbeat_interval"] = 30 * 60


@given("lastMoltbookCheck is 10 minutes ago")
def step_last_check_10(context):
    now = time.time()
    context.kv_store.set("lastMoltbookCheck", now - 10 * 60)
    _state(context)["now"] = now


@given("lastMoltbookCheck is 31 minutes ago")
def step_last_check_31(context):
    now = time.time()
    context.kv_store.set("lastMoltbookCheck", now - 31 * 60)
    _state(context)["now"] = now


@when("the runtime heartbeat loop runs")
def step_run_heartbeat(context):
    interval = _state(context).get("heartbeat_interval", 30 * 60)
    now = _state(context).get("now", time.time())
    result = run_heartbeat(
        context.app,
        context.kv_store,
        now_fn=lambda: now,
        interval_seconds=interval,
    )
    _state(context)["heartbeat_result"] = result


@then("the runtime skips feed checks")
def step_skips_checks(context):
    assert _state(context)["heartbeat_result"]["ran"] is False


@then("the runtime fetches the feed endpoints")
def step_fetches_feeds(context):
    result = _state(context)["heartbeat_result"]
    assert result["ran"] is True
    assert result["feeds_checked"]


@then("the runtime performs semantic search")
def step_search_performed(context):
    assert _state(context)["heartbeat_result"]["search_performed"] is True


@then("the runtime updates lastMoltbookCheck")
def step_updates_last_check(context):
    assert context.kv_store.get("lastMoltbookCheck") is not None


@given('an idempotency key "{op_id}" mapped to post_id "{post_id}"')
def step_idempotent_mapping(context, op_id, post_id):
    context.kv_store.set(f"op:post:{op_id}", post_id)


@given("the social platform has 0 posts")
def step_platform_zero_posts(context):
    assert len(context.social_platform.posts) == 0


@when('the runtime attempts to create a post with idempotency key "{op_id}"')
def step_create_post_idempotent(context, op_id):
    post_id = context.app.create_post_idempotent(
        op_id,
        submolt="general",
        title="Title",
        content="Content",
    )
    _state(context)["created_post_id"] = post_id


@then('the existing post_id "{post_id}" is returned')
def step_existing_post_returned(context, post_id):
    assert _state(context)["created_post_id"] == post_id


@then("no new post is created")
def step_no_new_post(context):
    assert len(context.social_platform.posts) == 0


@given('no idempotency mapping for "{op_id}"')
def step_no_mapping(context, op_id):
    context.kv_store.set(f"op:post:{op_id}", None)


@then('a new post_id is created and stored for "{op_id}"')
def step_new_post_created(context, op_id):
    post_id = _state(context)["created_post_id"]
    assert post_id
    assert context.kv_store.get(f"op:post:{op_id}") == post_id
    assert len(context.social_platform.posts) == 1
