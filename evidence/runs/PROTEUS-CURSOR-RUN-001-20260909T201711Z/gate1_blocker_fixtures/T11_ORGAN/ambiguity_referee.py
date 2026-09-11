"""LLM-native judgment boundary for short, ambiguous support messages.

`AmbiguityReferee` deliberately has no keyword table, intent switch, or transition
graph.  Each call delegates interpretation to the supplied `LLMJudge`; production
runtime code is responsible for adapting its transformer/API client to that
interface.

The dataclasses below are a transport boundary, not a model of the whole support
situation.  They cannot capture the customer's unstated context, organization
history, tone, stakes, or every plausible interpretation.  In particular,
`uncertainty` is the judge's expressed uncertainty, not a calibrated fact.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Protocol, Sequence


Action = Literal[
    "ask_clarifying_question", "offer_reversible_step", "respond_with_assumption"
]


@dataclass(frozen=True)
class Interpretation:
    """One reading proposed by the LLM judgment call."""

    reading: str
    plausibility: float


@dataclass(frozen=True)
class AmbiguityJudgment:
    """A deliberately small, reopenable representation of a judgment."""

    interpretations: tuple[Interpretation, ...]
    uncertainty: float
    recommended_action: Action
    clarification_question: str | None
    rationale: str


class LLMJudge(Protocol):
    """Interface an LLM/transformer adapter must implement in the runtime."""

    def __call__(self, *, message: str, instruction: str) -> Mapping[str, object]: ...


class AmbiguityReferee:
    """Obtain a fresh LLM judgment rather than routing from surface keywords."""

    _INSTRUCTION = """You are resolving ambiguity in a short support message.
Do not pretend ambiguity is absent. Return a mapping with:
- interpretations: a non-empty list of {reading, plausibility} alternatives;
- uncertainty: number from 0 to 1 representing your remaining uncertainty;
- recommended_action: ask_clarifying_question, offer_reversible_step, or
  respond_with_assumption;
- clarification_question: a question or null; and rationale: brief explanation.
Favor a clarification question when material interpretations remain live."""

    def __init__(self, judge: LLMJudge) -> None:
        self._judge = judge

    def judge(self, message: str) -> AmbiguityJudgment:
        """Invoke the LLM-shaped callable and preserve its uncertainty explicitly."""
        if not message or not message.strip():
            raise ValueError("message must be non-empty")
        raw = self._judge(message=message, instruction=self._INSTRUCTION)
        return self._coerce(raw)

    @staticmethod
    def _coerce(raw: Mapping[str, object]) -> AmbiguityJudgment:
        try:
            uncertainty = float(raw["uncertainty"])
            action = raw["recommended_action"]
            rows = raw["interpretations"]
            question = raw.get("clarification_question")
            rationale = raw["rationale"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("LLM judge returned an incomplete judgment") from exc

        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError("uncertainty must be between 0 and 1")
        if action not in {
            "ask_clarifying_question",
            "offer_reversible_step",
            "respond_with_assumption",
        }:
            raise ValueError("unrecognized recommended_action")
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
            raise ValueError("interpretations must be a non-empty sequence")

        interpretations: list[Interpretation] = []
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError("each interpretation must be a mapping")
            reading = row.get("reading")
            plausibility = row.get("plausibility")
            if not isinstance(reading, str) or not reading.strip():
                raise ValueError("interpretation reading must be non-empty")
            try:
                score = float(plausibility)
            except (TypeError, ValueError) as exc:
                raise ValueError("interpretation plausibility must be numeric") from exc
            if not 0.0 <= score <= 1.0:
                raise ValueError("interpretation plausibility must be between 0 and 1")
            interpretations.append(Interpretation(reading, score))

        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("rationale must be non-empty")
        if question is not None and (not isinstance(question, str) or not question.strip()):
            raise ValueError("clarification_question must be a non-empty string or null")
        if action == "ask_clarifying_question" and question is None:
            raise ValueError("clarifying action requires a clarification_question")

        return AmbiguityJudgment(
            interpretations=tuple(interpretations),
            uncertainty=uncertainty,
            recommended_action=action,  # type: ignore[arg-type]
            clarification_question=question,
            rationale=rationale,
        )
