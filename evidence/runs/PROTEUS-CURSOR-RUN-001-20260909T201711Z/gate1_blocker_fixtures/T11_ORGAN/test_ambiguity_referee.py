import unittest

from ambiguity_referee import AmbiguityReferee


class RecordingLLMJudge:
    """A runtime-shaped stand-in: its output is not inferred from message words."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def __call__(self, *, message: str, instruction: str) -> dict[str, object]:
        self.calls.append((message, instruction))
        return {
            "interpretations": [
                {"reading": "The customer cannot access an account.", "plausibility": 0.47},
                {"reading": "The customer wants a prior item restored.", "plausibility": 0.44},
            ],
            "uncertainty": 0.82,
            "recommended_action": "ask_clarifying_question",
            "clarification_question": "Do you mean account access, or restoring a previous item?",
            "rationale": "Both readings remain plausible from the available message.",
        }


class AmbiguityRefereeTests(unittest.TestCase):
    def test_invokes_judgment_callable_and_preserves_high_uncertainty(self) -> None:
        model = RecordingLLMJudge()
        referee = AmbiguityReferee(model)

        judgment = referee.judge("I can't get into it after we changed it. Can you restore it?")

        self.assertEqual(len(model.calls), 1)
        self.assertIn("resolving ambiguity", model.calls[0][1])
        self.assertGreaterEqual(judgment.uncertainty, 0.8)
        self.assertEqual(judgment.recommended_action, "ask_clarifying_question")
        self.assertEqual(len(judgment.interpretations), 2)

        # A keyword router that sees only "get into" or "restore" and emits a
        # confident canned route would fail this: the organ must invoke judgment
        # and retain the unresolved alternatives and uncertainty.


if __name__ == "__main__":
    unittest.main()
