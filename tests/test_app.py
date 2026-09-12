import hashlib
import re

import numpy as np

import app


class HashingEmbedder:
    dimensions = 128

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        rows = []
        for text in texts:
            vector = np.zeros(self.dimensions, dtype=float)
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % self.dimensions
                vector[index] += 1.0
            rows.append(vector)
        return np.vstack(rows)


def test_gradio_demo_builds_without_loading_embedding_model():
    assert app.demo is not None
    assert len(app.BASELINE_MEMORY_DATA) == 8


def test_business_presentation_is_centered_and_privacy_first():
    assert "max-width: 1080px" in app.APP_CSS
    assert "without storing everything forever" in app.HERO_HTML
    assert "Public-demo privacy boundary" in app.HERO_HTML
    assert "SAVE / SKIP / BLOCK" in app.CONCEPT_HTML


def test_primary_interaction_uses_explicit_light_control_styling():
    assert "#memory-query textarea" in app.APP_CSS
    assert ".answer-panel" in app.APP_CSS
    assert "#run-memory-request" in app.APP_CSS
    assert "background: #ffffff" in app.APP_CSS
    assert "color: #0f172a" in app.APP_CSS


def test_business_story_explains_enterprise_pilot_continuity_problem():
    assert "enterprise customer pilot" in app.BUSINESS_STORY_HTML
    assert "Support, Operations, and Engineering" in app.BUSINESS_STORY_HTML
    assert "Business risk" in app.BUSINESS_STORY_HTML
    assert "Application authority" in app.BUSINESS_STORY_HTML


def test_public_evidence_uses_light_html_tables_not_native_dataframe():
    html = app.format_memory_html(app.fresh_baseline_memory_data())
    assert "evidence-table" in html
    assert "Harborlight Support Portal" in html
    assert "gr.Dataframe" not in open("app.py", encoding="utf-8").read()


def test_stream_session_exposes_real_memory_activity_and_business_outcome(monkeypatch):
    monkeypatch.setattr(app, "get_embedding_model", lambda: HashingEmbedder())
    frames = list(
        app.stream_session(
            "What did we decide about the enterprise pilot prerequisites?",
            4,
            True,
            app.fresh_baseline_memory_data(),
            [],
        )
    )
    assert len(frames) >= 6
    assert "RUNNING" in frames[0][0]
    assert "Relevant memories retrieved" in "".join(frame[0] for frame in frames)
    assert "Memory policy evaluated" in "".join(frame[0] for frame in frames)
    assert "COMPLETE" in frames[-1][0]
    assert "SKIP" in frames[-1][4]
    assert "What Harborlight carried forward" in frames[-1][2]
    assert "Memory governance" in frames[-1][2]


def test_reset_session_restores_synthetic_baseline():
    result = app.reset_session()
    memory_state = result[-2]
    audit_state = result[-1]
    assert len(memory_state) == 8
    assert audit_state == []
