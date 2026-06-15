from agent.memory import Memory


def test_memory_keeps_bounded_history() -> None:
    memory = Memory("test goal")
    for idx in range(20):
        memory.add_action(
            {"thought": f"step {idx}", "tool": "wait", "args": {"ms": idx}},
            {"ok": True, "message": "ok", "data": {}},
        )
    payload = memory.to_prompt_payload()
    assert len(memory.history) == 8
    assert len(payload["recent_history"]) == 8
    assert payload["recent_history"][0]["step"] == 13


def test_facts_merge_and_values_are_strings() -> None:
    import tempfile
    import os

    fd, path = tempfile.mkstemp()
    os.close(fd)
    try:
        memory = Memory("test goal", db_path=path)
        memory.merge_facts({"answer": 42, "name": "Ada"})
        memory.merge_facts({"answer": "updated"})
        assert memory.facts == {"answer": "updated", "name": "Ada"}
    finally:
        os.remove(path)


def test_prompt_payload_truncates_large_observation() -> None:
    memory = Memory("test goal")
    memory.update_observation(
        {
            "url": "https://example.test",
            "title": "Example",
            "snapshot_yaml": "x" * 20000,
            "body_text": "y" * 10000,
        }
    )
    payload = memory.to_prompt_payload()
    assert payload["current_page"]["url"] == "https://example.test"
    assert len(payload["current_page"]["snapshot_yaml"]) < 12200
    assert len(payload["current_page"]["body_text_excerpt"]) < 6200


def test_merge_facts_with_none() -> None:
    import tempfile
    import os

    fd, path = tempfile.mkstemp()
    os.close(fd)

    try:
        memory = Memory("test goal", db_path=path)
        memory.merge_facts(None)
        assert memory.facts == {}
    finally:
        os.remove(path)


def test_merge_facts_db_persistence() -> None:
    import sqlite3
    import tempfile
    import os

    fd, path = tempfile.mkstemp()
    os.close(fd)

    try:
        memory1 = Memory("test goal", db_path=path)
        memory1.merge_facts({"test_key": "test_value", "number": 123})

        # Verify in memory state
        assert memory1.facts == {"test_key": "test_value", "number": "123"}

        # Verify DB state directly
        with sqlite3.connect(path) as conn:
            cursor = conn.execute("SELECT key, value FROM facts ORDER BY key")
            rows = cursor.fetchall()
            assert rows == [("number", "123"), ("test_key", "test_value")]

        # Verify across instances
        memory2 = Memory("test goal", db_path=path)
        assert memory2.facts == {"test_key": "test_value", "number": "123"}

        # Update existing and add new
        memory2.merge_facts({"test_key": "updated_value", "new_key": "new_value"})

        # Verify in memory state
        assert memory2.facts == {
            "test_key": "updated_value",
            "number": "123",
            "new_key": "new_value",
        }

        # Verify DB state directly again
        with sqlite3.connect(path) as conn:
            cursor = conn.execute("SELECT key, value FROM facts ORDER BY key")
            rows = cursor.fetchall()
            assert rows == [
                ("new_key", "new_value"),
                ("number", "123"),
                ("test_key", "updated_value"),
            ]
    finally:
        os.remove(path)


def test_merge_facts_truncation() -> None:
    import tempfile
    import os

    fd, path = tempfile.mkstemp()
    os.close(fd)

    try:
        memory = Memory("test goal", db_path=path)
        long_value = "x" * 2000
        memory.merge_facts({"long_fact": long_value})

        # Verify it was truncated
        stored_value = memory.facts["long_fact"]
        assert len(stored_value) <= 1014  # 1000 + len("...[truncated]")
        assert stored_value.endswith("...[truncated]")
        assert stored_value.startswith("x" * 1000)
    finally:
        os.remove(path)
