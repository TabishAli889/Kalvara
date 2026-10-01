from tests.conftest import FakeProvider


def test_health(make_client):
    client = make_client(FakeProvider("ollama", local=True))
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_models_lists_local_first_and_picks_local_default(make_client):
    client = make_client(
        FakeProvider("ollama", local=True, models=["llama3.2:latest", "qwen3:8b"]),
        FakeProvider("openai", models=["gpt-x"]),
    )
    body = client.get("/api/models").json()
    assert [p["id"] for p in body["providers"]] == ["ollama", "openai"]
    assert body["has_local_models"] is True
    assert body["default"] == {
        "id": "llama3.2:latest",
        "name": "llama3.2:latest",
        "provider": "ollama",
        "local": True,
        "size_bytes": None,
        "parameter_size": None,
        "family": None,
        "vision": False,
    }
    assert body["default_vision"] is None


def test_models_default_is_cloud_when_no_local_models(make_client):
    client = make_client(
        FakeProvider("ollama", local=True, models=[]),
        FakeProvider("anthropic", models=["claude-a", "claude-b"], default_model="claude-b"),
    )
    body = client.get("/api/models").json()
    assert body["has_local_models"] is False
    assert body["default"]["provider"] == "anthropic"
    assert body["default"]["id"] == "claude-b"


def test_models_reports_unreachable_and_unconfigured_providers(make_client):
    client = make_client(
        FakeProvider("ollama", local=True, list_error="Ollama is not reachable"),
        FakeProvider("gemini", configured=False),
    )
    providers = {p["id"]: p for p in client.get("/api/models").json()["providers"]}
    assert providers["ollama"]["available"] is False
    assert providers["ollama"]["error"] == "Ollama is not reachable"
    assert providers["gemini"]["configured"] is False
    assert providers["gemini"]["available"] is False


def test_models_default_skips_preview_and_task_specific_builds(make_client):
    """Providers list previews and task-specific builds beside chat models.

    Google's list starts with `antigravity-preview-*`, so picking the first id
    yields a model that cannot serve a chat request.
    """
    client = make_client(
        FakeProvider("ollama", local=True, models=[]),
        FakeProvider(
            "gemini",
            models=[
                "antigravity-preview-05-2026",
                "deep-research-pro-preview-12-2025",
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-pro-latest",
            ],
        ),
    )
    body = client.get("/api/models").json()
    assert body["default"]["id"] == "gemini-flash-latest"


def test_models_default_prefers_latest_alias_over_pinned_version(make_client):
    client = make_client(
        FakeProvider("ollama", local=True, models=[]),
        FakeProvider("gemini", models=["gemini-3.6-flash", "gemini-flash-latest"]),
    )
    assert client.get("/api/models").json()["default"]["id"] == "gemini-flash-latest"


def test_models_explicit_default_model_still_wins(make_client):
    """An operator's GEMINI_MODEL overrides the heuristic, even for a preview."""
    client = make_client(
        FakeProvider("ollama", local=True, models=[]),
        FakeProvider(
            "gemini",
            models=["gemini-flash-latest", "gemini-3-flash-preview"],
            default_model="gemini-3-flash-preview",
        ),
    )
    assert client.get("/api/models").json()["default"]["id"] == "gemini-3-flash-preview"


def test_models_default_falls_back_to_first_when_all_are_niche(make_client):
    """Never return nothing just because every id looks niche."""
    client = make_client(
        FakeProvider("ollama", local=True, models=[]),
        FakeProvider("gemini", models=["alpha-preview-1", "beta-preview-2"]),
    )
    assert client.get("/api/models").json()["default"]["id"] == "alpha-preview-1"
