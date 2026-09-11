# F05 project capsule episode

Date: 2026-09-11

## Bounded capability

Added `python -m proteus capsule --project <existing-project> --out <capsule.md>`.
It creates one bounded Markdown handoff artifact without writing to the selected
project. The artifact records observable Git state, runtime manifests, required
instructions, and prioritized excerpts of standard current-state and roadmap
carriers. It is intentionally not an archive or transcript.

## Exercise target

Selected `C:\projects\multiagent-moderation-env` (selection rationale:
`F05_PROJECT_SELECTION.md`). The generated artifact is
`F05_MULTIAGENT_MODERATION_PROJECT_CAPSULE.md`.

Final generation observation:

- 38,527 Unicode characters (45,949 UTF-8 bytes), substantially smaller than
  the target tree.
- The target had 4,207 non-dependency/cache files by the capsule's inventory.
- Git observation: `main` at `e52389098cb21d9d65a6998702253a7535e25872`,
  dirty with 3,075 paths.
- The capsule separated 324 non-cache-shaped paths from 2,751
  browser/cache-shaped paths; it did not classify either group as safe to
  delete.

## Independent receiver

An independent `codex exec --ephemeral` receiver was launched with no resume,
fork, or prior transcript. Its only supplied project-context artifact was the
first generated capsule; it was explicitly asked not to inspect source or
modify the target. Input: `F05_CAPSULE_RECEIVER_PROMPT.txt`; raw preserved
answer: `F05_CAPSULE_RECEIVER_RAW_RESULT.txt`; launch receipt:
`F05_CAPSULE_RECEIVER_META.json`.

The receiver correctly understood the product as a FastAPI/SQLAlchemy/Postgres
Next.js moderator workspace and identified dirty work, stale/conflicting
roadmap signals, production LLM gating, and the need to inspect governing docs,
diffs, owning modules, smoke scripts, and the master recovery plan before a
change.

## Causal repair after receiver review

The first capsule's first-80 Git-path listing was dominated by browser profile
and cache artifacts, obscuring the actionable dirty set. Also, the roadmap
named `RECOVERY_REENTRY_MASTER_PLAN_v2_3_to_v3_4.md` as its source of truth but
the capsule did not include it. The implementation now:

1. summarizes browser/cache-shaped dirty paths separately while keeping an
   explicit warning that they are not presumed disposable;
2. prioritizes mandatory AGENTS/operations/product-law documents; and
3. includes the named master recovery plan before the roadmap excerpt.

The repaired final capsule was regenerated at the path above. The raw receiver
answer remains untouched as the first-pass evaluation record. The receiver's
input observed 3,075 expanded dirty paths. A later read-only target status check
observed 64 paths after the transient browser/cache-shaped set disappeared. The
final implementation now asks Git to summarize untracked directories, avoiding
this volatile cache expansion entirely. This capability did not delete or alter
target files.

## Validation

- `python tests/test_capsule.py` — PASS
- `python -m pytest -q` — 50 passed
- `python -m proteus capsule --help` — PASS
- `git diff --check` — PASS (only line-ending warnings)

## Known boundaries

- Standard document names are intentionally prioritized; unusual project-local
  state carriers require adding a candidate or inspecting source directly.
- Redaction is heuristic and must never be treated as a permission to include
  secrets in a capsule.
- The capsule exposes Git paths and document excerpts, not diff bodies or
  untracked-file contents. A receiver still must inspect relevant source before
  editing.
- The target's current-state documents contain historical and conflicting
  sequencing. The capsule identifies this instead of selecting a false single
  truth.
