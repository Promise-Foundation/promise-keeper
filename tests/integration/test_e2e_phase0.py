from pkc.adapters.moltbook.memory_platform import InMemorySocialPlatform
from pkc.adapters.persistence.memory_event_log import InMemoryEventLog
from pkc.adapters.persistence.memory_kv import InMemoryKVStore
from pkc.app.facade import Application
from pkc.runtime.heartbeat import run_heartbeat


def test_phase0_card_command_and_heartbeat() -> None:
    social = InMemorySocialPlatform()
    events = InMemoryEventLog()
    kv = InMemoryKVStore()
    app = Application(social_platform=social, event_log=events, kv_store=kv)

    post_id = app.create_post("general", "Title", "Content")
    result = app.handle_card_command(
        post_id=post_id,
        promiser_id="@agent",
        commitment_text="I will deliver X",
        success_criteria="X delivered",
        evidence_plan="artifact_cid",
        assessment_window="W1",
    )

    assert result["comment_id"]
    assert result["promise_card_cid"]
    assert app.get_cid_for_moltbook(result["comment_id"]) == result["promise_card_cid"]

    heartbeat_result = run_heartbeat(app, kv, now_fn=lambda: 1_000_000, interval_seconds=30 * 60)
    assert heartbeat_result["ran"] is True
    assert kv.get("lastMoltbookCheck") == 1_000_000
