"""Create a compact, source-grounded handoff capsule for a coding project.

The capsule deliberately collects only durable entry material and observable git
state.  It is not an archive and it does not attempt to infer a task from an
agent transcript.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MAX_CHARS = 48_000
IGNORED_DIRS = {".git", ".next", "node_modules", ".venv", "__pycache__"}

# Ordered from mandatory project instructions through likely current-work
# carriers.  A missing file is normal; projects vary widely.
DOCUMENT_CANDIDATES = (
    ("Project instructions", "AGENTS.md", 3_000),
    ("Project instructions", "CLAUDE.md", 3_000),
    ("Operations constraints", "docs/ops/PRODUCTION_TOPOLOGY_AND_GATES.md", 4_500),
    ("Product law", "docs/product/MODERATOR_COCKPIT_INTERFACE_LAW_v0_1.md", 5_000),
    ("Project overview", "README.md", 3_000),
    ("Current-state carrier", "CURRENT.md", 5_000),
    ("Current-state carrier", "FRONTIER.md", 5_000),
    ("Current-state carrier", "PROJECT_INTENT_AND_CURRENT_STATE.md", 7_000),
    ("Current plan referenced by roadmap", "RECOVERY_REENTRY_MASTER_PLAN_v2_3_to_v3_4.md", 6_000),
    ("Roadmap / next work", "ROADMAP_NEXT_STEPS.md", 5_000),
    ("Handoff", "HANDOFF.md", 5_000),
    ("Contribution guide", "CONTRIBUTING.md", 4_000),
)
MANIFEST_CANDIDATES = (
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "backend/requirements.txt",
    "frontend/package.json",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
)


def _run(project: Path, *args: str) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=project,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return completed.returncode, completed.stdout.strip()


def _redact(text: str) -> str:
    """Remove common credential forms before a capsule is written."""
    patterns = (
        r"(?i)(api[_-]?key|token|password|secret)\s*([=:])\s*[^\s'\"`]+",
        r"\bsk-[A-Za-z0-9_-]{12,}\b",
        r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
    )
    for pattern in patterns:
        text = re.sub(pattern, "<REDACTED>", text)
    return text


def _excerpt(path: Path, limit: int) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"[Could not read: {exc}]"
    # Do not carry source Markdown's trailing double-space line-break markers:
    # they add no handoff meaning and make generated artifacts fail whitespace
    # validation.
    text = "\n".join(line.rstrip() for line in _redact(text).splitlines()).strip()
    if len(text) <= limit:
        return text
    # Keep the beginning, which normally contains scope and instructions, and
    # label the loss so a receiver does not mistake it for a complete document.
    return text[:limit].rstrip() + f"\n\n[Excerpt truncated at {limit:,} characters; inspect {path.name} before relying on omitted detail.]"


def _count_files(project: Path) -> int:
    count = 0
    for path in project.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file():
            count += 1
    return count


def _git_state(project: Path) -> tuple[list[str], str, str]:
    code, root = _run(project, "git", "rev-parse", "--show-toplevel")
    if code:
        return [], "Not a Git repository (or git unavailable).", ""
    _, branch = _run(project, "git", "branch", "--show-current")
    _, head = _run(project, "git", "log", "-1", "--format=%H")
    _, log = _run(project, "git", "log", "-8", "--date=short", "--format=%h %ad %s")
    # `normal` intentionally collapses untracked directories.  Expanding every
    # untracked browser profile can turn a compact handoff into thousands of
    # volatile cache paths, while the receiver still knows the tree is dirty.
    _, porcelain = _run(project, "git", "status", "--porcelain=v1", "--untracked-files=normal")
    changed = porcelain.splitlines() if porcelain else []

    def cache_shaped(entry: str) -> bool:
        candidate = entry[3:].replace("\\", "/").lower()
        return any(
            marker in candidate
            for marker in (
                "/.edge-render-",
                "/crashpad/",
                "/cache/",
                "/code cache/",
                "/gpucache/",
                "/dawngraphitecache/",
                "/dawnwebgpucache/",
            )
        )

    cache_paths = [entry for entry in changed if cache_shaped(entry)]
    actionable = [entry for entry in changed if entry not in cache_paths]
    status = [
        f"Git root: `{root}`",
        f"Branch: `{branch or '(detached HEAD)'}`",
        f"HEAD: `{head or '(unavailable)'}`",
        f"Working tree: {'clean' if not changed else f'dirty ({len(changed)} status entries; untracked directories summarized)'}",
    ]
    if changed:
        status.append(
            f"Changed-path triage: {len(actionable)} non-cache-shaped paths; "
            f"{len(cache_paths)} browser/cache-shaped paths (not assumed disposable)."
        )
        shown = actionable[:80]
        if shown:
            status.append("Non-cache-shaped changed paths (porcelain; inspect before editing):\n```text\n" + "\n".join(shown) + "\n```")
        if len(actionable) > len(shown):
            status.append(f"[Only first {len(shown)} of {len(actionable)} non-cache-shaped paths shown.]")
        if cache_paths:
            status.append(
                "[Browser/cache-shaped paths are summarized to keep the handoff legible; "
                "they remain part of the dirty tree and must not be deleted blindly.]"
            )
    return status, log or "(No commits found.)", branch


@dataclass(frozen=True)
class CapsuleResult:
    project: Path
    output: Path
    chars: int
    included_documents: tuple[str, ...]


def build_capsule(project: Path, output: Path, *, max_chars: int = DEFAULT_MAX_CHARS) -> CapsuleResult:
    """Write one Markdown capsule.  Does not mutate *project*."""
    project = project.expanduser().resolve()
    output = output.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project is not a directory: {project}")
    if max_chars < 4_000:
        raise ValueError("max_chars must be at least 4000")

    git_state, recent_log, branch = _git_state(project)
    top_level = sorted(p.name + ("/" if p.is_dir() else "") for p in project.iterdir() if p.name not in IGNORED_DIRS)
    lines = [
        "# Project Capsule",
        "",
        "> Generated context, not a source of truth. Verify cited files and current Git state before changing the project.",
        "",
        "## Receiver protocol",
        "",
        "1. Treat the project instructions and constraints below as binding.",
        "2. Preserve existing dirty work: inspect it before editing or cleaning anything.",
        "3. Reconcile any conflicting roadmap/current-state material by checking Git history and the cited source files.",
        "4. Before implementation, read the listed files most relevant to the chosen change and run the narrowest documented check.",
        "",
        "## Observed repository",
        "",
        f"- Project: `{project}`",
        f"- Generated (UTC): `{datetime.now(timezone.utc).isoformat()}`",
        f"- Approximate tracked/working source files (excluding common dependency/cache directories): {_count_files(project):,}",
        f"- Top level: {', '.join(f'`{name}`' for name in top_level[:60])}" + (" …" if len(top_level) > 60 else ""),
        "",
        "## Git working situation",
        "",
        *git_state,
        "",
        "### Recent commits",
        "",
        "```text",
        recent_log,
        "```",
        "",
        "## Runtime / build manifests",
        "",
    ]
    for rel in MANIFEST_CANDIDATES:
        path = project / rel
        if path.is_file():
            lines.extend((f"### `{rel}`", "", "```text", _excerpt(path, 3_000), "```", ""))

    included: list[str] = []
    # Reserve room for headings and the source map. Individual excerpts are
    # additionally bounded; the global check below never silently overflows.
    for category, rel, limit in DOCUMENT_CANDIDATES:
        path = project / rel
        if not path.is_file():
            continue
        remaining = max_chars - len("\n".join(lines)) - 1_600
        if remaining < 500:
            break
        excerpt = _excerpt(path, min(limit, max(500, remaining)))
        lines.extend((f"## {category}: `{rel}`", "", excerpt, ""))
        included.append(rel)

    lines.extend((
        "## What to inspect before changing code",
        "",
        "- The mandatory instruction files above, plus any documents named by them for the surface you will change.",
        "- The current diff for every dirty path that overlaps your task; do not assume it is disposable.",
        "- The owning backend/frontend module and its nearest existing smoke or test script.",
        "- Deployment/production gates before touching deploy, Caddy, provider configuration, or a manual-test gate.",
        "",
        "## Capsule boundaries",
        "",
        "- This is a compact index and excerpts, not an archive, a transcript, or a substitute for source inspection.",
        "- It intentionally omits untracked file contents, Git diff bodies, binaries, dependency trees, and environment files.",
        "- Common credential-shaped values are redacted heuristically; never treat a capsule as a safe place for secrets.",
        "- `current` and `next` claims remain attributed to the included documents and Git observation; documents can be stale or conflict.",
        "",
        "## Included source map",
        "",
        *[f"- `{item}`" for item in included],
    ))
    text = "\n".join(lines).rstrip() + "\n"
    if len(text) > max_chars:
        # This should be rare because documents are budgeted. Preserve a valid,
        # explicitly incomplete result instead of failing after expensive scan.
        text = text[: max_chars - 120].rstrip() + "\n\n[Capsule reached global size limit; inspect project files directly.]\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return CapsuleResult(project=project, output=output, chars=len(text), included_documents=tuple(included))
