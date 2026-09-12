import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".json", ".csv", ".txt", ".yml", ".yaml", ".toml"}

# Build private-source markers from pieces so this test does not itself contain the
# exact strings it is designed to reject from public artifacts.
FORBIDDEN_TEXT = [
    "Agent Engineering Master " + "Curriculum",
    "agent_eng_" + "curriculum",
    "30 Agents for AI " + "Engineers",
]

FORBIDDEN_FILENAMES = {
    "WORKING_METHOD.md",
    "memory_agent_audit_log.csv",
}

SECRET_PATTERNS = {
    "hugging_face_token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "github_classic_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "github_fine_grained_token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "openai_style_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def tracked_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name == ".gitignore":
            yield path


def test_forbidden_private_source_files_are_not_present():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        assert path.name not in FORBIDDEN_FILENAMES, f"Forbidden public artifact: {relative}"
        if path.name != ".gitignore":
            assert "curriculum" not in str(relative).lower(), f"Private-source path detected: {relative}"


def test_private_source_markers_are_not_in_public_text_files():
    violations = []
    for path in tracked_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in FORBIDDEN_TEXT:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT)} contains private-source marker")
    assert not violations, "\n".join(violations)


def test_common_secret_formats_are_not_committed():
    violations = []
    for path in tracked_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                violations.append(f"{path.relative_to(ROOT)} matched {label}")
    assert not violations, "\n".join(violations)
