import re
from typing import List

from schemas import MemoryWriteDecision


_SENSITIVE_PATTERNS = {
    "credential": [
        r"\bpassword\b",
        r"\bpasscode\b",
        r"\bapi[ _-]?key\b",
        r"\baccess[ _-]?token\b",
        r"\brefresh[ _-]?token\b",
        r"\bprivate[ _-]?key\b",
        r"\bsecret[ _-]?key\b",
        r"\bbearer[ _-]?token\b",
    ],
    "identity": [
        r"\bsocial security\b",
        r"\bssn\b",
        r"\bpassport\b",
    ],
    "financial": [
        r"\bcredit card\b",
        r"\bcard number\b",
        r"\brouting number\b",
        r"\bbank account\b",
        r"\bbrokerage account\b",
    ],
    "health": [
        r"\bmedical record\b",
        r"\bmedical history\b",
        r"\bdiagnosis\b",
    ],
    "confidential_client": [
        r"\bconfidential client\b",
        r"\bclient account\b",
        r"\bclient portfolio\b",
    ],
    "email_address": [
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    ],
}

_DURABLE_MARKERS = (
    "remember",
    "we decided",
    "the team decided",
    "scheduled",
    "deadline",
    "due date",
    "must",
    "should",
    "owns",
    "owner",
    "prefer",
    "preference",
    "launch date",
)

_QUESTION_PREFIXES = ("what ", "when ", "who ", "where ", "why ", "how ", "can ", "do ", "does ")


def detect_sensitive_content(text: str) -> List[str]:
    flags: List[str] = []
    for category, patterns in _SENSITIVE_PATTERNS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            flags.append(category)
    return flags


def _normalize_memory_statement(text: str) -> str:
    statement = text.strip()
    lowered = statement.lower()
    prefix = "remember that "
    if lowered.startswith(prefix):
        statement = statement[len(prefix):].strip()
    if statement and statement[-1] not in ".!?":
        statement += "."
    if statement:
        statement = statement[0].upper() + statement[1:]
    return statement


def evaluate_memory_write(user_query: str) -> MemoryWriteDecision:
    query = (user_query or "").strip()
    if not query:
        return MemoryWriteDecision(
            outcome="skip",
            should_save=False,
            reason="Empty input does not create a durable memory.",
        )

    flags = detect_sensitive_content(query)
    if flags:
        return MemoryWriteDecision(
            outcome="block",
            should_save=False,
            reason="The public demo does not store content that appears sensitive or credential-like.",
            policy_flags=flags,
        )

    lowered = query.lower()
    explicit_memory_request = lowered.startswith("remember")
    looks_like_question = lowered.startswith(_QUESTION_PREFIXES) or query.endswith("?")
    durable_marker = any(marker in lowered for marker in _DURABLE_MARKERS)

    if looks_like_question and not explicit_memory_request:
        return MemoryWriteDecision(
            outcome="skip",
            should_save=False,
            reason="A retrieval question is useful for this turn but is not itself durable project memory.",
        )

    if not durable_marker:
        return MemoryWriteDecision(
            outcome="skip",
            should_save=False,
            reason="The interaction does not contain a clear durable decision, preference, owner, schedule, or explicit remember request.",
        )

    memory_type = "semantic" if any(term in lowered for term in ("prefer", "preference", "owns", "owner")) else "episodic"
    importance = 5 if any(term in lowered for term in ("must", "deadline", "launch date", "we decided", "the team decided")) else 4

    return MemoryWriteDecision(
        outcome="save",
        should_save=True,
        memory_type=memory_type,
        importance=importance,
        reason="The interaction contains a durable, public-demo-safe project decision or preference.",
        proposed_memory=_normalize_memory_statement(query),
    )
