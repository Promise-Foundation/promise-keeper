from pkc.adapters.moltbook.memory_platform import InMemorySocialPlatform


def test_social_platform_contract_minimal() -> None:
    platform = InMemorySocialPlatform()

    post_id = platform.create_post("general", "Title", "Content")
    assert post_id

    comment_id = platform.create_comment(post_id, "Hello")
    assert comment_id

    feed = list(platform.fetch_feed("/feed?sort=new"))
    assert any(p.get("id") == post_id for p in feed)

    results = list(platform.search("Content"))
    assert any(p.get("id") == post_id for p in results)

    platform.delete_post(post_id)
    feed_after = list(platform.fetch_feed("/feed?sort=new"))
    assert not any(p.get("id") == post_id for p in feed_after)
