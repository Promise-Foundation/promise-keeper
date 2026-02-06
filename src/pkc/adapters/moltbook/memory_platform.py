from __future__ import annotations

from pkc.ports.social_platform import SocialPlatformPort


class InMemorySocialPlatform(SocialPlatformPort):
    def __init__(self) -> None:
        self._post_counter = 0
        self._comment_counter = 0
        self.posts: dict[str, dict] = {}
        self.comments: dict[str, dict] = {}

    def create_post(self, submolt: str, title: str, content: str) -> str:
        self._post_counter += 1
        post_id = f"post_{self._post_counter}"
        self.posts[post_id] = {
            "id": post_id,
            "submolt": submolt,
            "title": title,
            "content": content,
        }
        return post_id

    def create_comment(self, post_id: str, content: str, parent_id: str | None = None) -> str:
        self._comment_counter += 1
        comment_id = f"comment_{self._comment_counter}"
        self.comments[comment_id] = {
            "id": comment_id,
            "post_id": post_id,
            "content": content,
            "parent_id": parent_id,
        }
        return comment_id

    def delete_post(self, post_id: str) -> None:
        self.posts.pop(post_id, None)

    def fetch_feed(self, endpoint: str):
        # For in-memory testing, return all posts
        return list(self.posts.values())

    def search(self, query: str, limit: int = 20):
        matches = []
        for post in self.posts.values():
            if query.lower() in post.get("content", "").lower():
                matches.append(post)
        return matches[:limit]

    def clear(self) -> None:
        self._post_counter = 0
        self._comment_counter = 0
        self.posts.clear()
        self.comments.clear()
