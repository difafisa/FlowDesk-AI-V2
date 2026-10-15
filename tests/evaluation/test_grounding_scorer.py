"""Phase 5 — grounding scorer: unit test dengan fake jev, tanpa API."""
from flowdesk.evaluation.grounding_scorer import score_answer


class FakeAns:
    def __init__(self, noul=None, choice=None):
        self.noul, self.choice = noul, choice


class FakeJev:
    def __init__(self, grounded=0.9, choice="correct", error=False):
        self.grounded, self.choice, self.error = grounded, choice, error
        self.captured = {}

    def judge(self, state, questions):
        self.captured = {"state": state, "questions": questions}
        if self.error:
            return None
        out = {"groundedness": FakeAns(noul=self.grounded)}
        if "correctness" in questions:
            out["correctness"] = FakeAns(choice=self.choice)
        return out


def test_scores_groundedness_only_without_reference():
    out = score_answer(FakeJev(grounded=0.85), "Jawaban.", "Evidence.")
    assert out["scored"] and out["groundedness"] == 0.85
    assert out["correctness"] is None


def test_correctness_included_when_reference_given():
    jev = FakeJev(choice="partial")
    out = score_answer(jev, "Jawaban.", "Evidence.", reference="Ref.")
    assert out["correctness"] == "partial"
    # keduanya SATU request
    assert set(jev.captured["questions"]) == {"groundedness", "correctness"}


def test_empty_answer_skipped():
    out = score_answer(FakeJev(), "", "Evidence.")
    assert not out["scored"] and out["error"] == "no_answer"


def test_api_failure_excluded_from_metrics():
    out = score_answer(FakeJev(error=True), "Jawaban.", "Evidence.")
    assert not out["scored"] and out["groundedness"] is None
    assert out["error"] == "api_failed"
