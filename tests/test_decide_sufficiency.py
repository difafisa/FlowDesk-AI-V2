"""Tahap 4 — tabel parametrik decide_sufficiency (pure, tanpa API).
Mencakup zona abu-abu, injection di rank 1, dan need_more."""
import pytest

from flowdesk.jev.decision import decide_sufficiency


def s(rel, ev, inj=0.0, ok=True):
    return {"is_relevant": rel, "contains_answer_evidence": ev,
            "contains_prompt_injection": inj, "ok": ok}


# (nama, scores, unscored_left, expected_decision)
CASES = [
    ("eligible -> sufficient",
     {"c1": s(0.9, 0.9)}, 0, "sufficient"),
    ("eligible di batas bawah (0.45/0.55 inklusif)",
     {"c1": s(0.45, 0.55)}, 0, "sufficient"),
    ("zona abu-abu: relevan tapi evidence kurang -> uncertain",
     {"c1": s(0.60, 0.40)}, 0, "uncertain"),
    ("zona abu-abu: relevant tepat di bawah 0.45 -> insufficient",
     {"c1": s(0.44, 0.90)}, 0, "insufficient"),
    ("semua tidak relevan -> insufficient",
     {"c1": s(0.10, 0.05), "c2": s(0.20, 0.10)}, 0, "insufficient"),
    ("relevan saja di antara yang tidak relevan -> uncertain",
     {"c1": s(0.10, 0.05), "c2": s(0.60, 0.30)}, 0, "uncertain"),
    ("injection di rank 1 membuang satu-satunya chunk layak -> insufficient",
     {"c1": s(0.95, 0.95, inj=0.90)}, 0, "insufficient"),
    ("injection dibuang, chunk layak lain tetap lolos -> sufficient",
     {"c1": s(0.95, 0.95, inj=0.90), "c2": s(0.80, 0.80)}, 0, "sufficient"),
    ("score error dicatat tidak layak -> insufficient",
     {"c1": s(0, 0, ok=False)}, 0, "insufficient"),
    ("belum sufficient + ada chunk belum terskor -> need_more",
     {"c1": s(0.10, 0.05)}, 3, "need_more"),
    ("sufficient mengalahkan unscored (spekulatif diterima)",
     {"c1": s(0.90, 0.90)}, 5, "sufficient"),
    ("kosong total -> insufficient",
     {}, 0, "insufficient"),
]


@pytest.mark.parametrize("name,scores,unscored,expected", CASES, ids=[c[0] for c in CASES])
def test_table(name, scores, unscored, expected):
    out = decide_sufficiency(scores, unscored_left=unscored)
    assert out["decision"] == expected


def test_injection_discard_recorded_with_reason():
    out = decide_sufficiency({"c1": s(0.95, 0.95, inj=0.90)})
    assert out["discarded"] == ["c1"]
    assert out["discard_reasons"] == {"c1": "injection"}


def test_score_error_recorded():
    out = decide_sufficiency({"c1": s(0, 0, ok=False)})
    assert out["discard_reasons"] == {"c1": "score_error"}


def test_sufficient_returns_included_ids():
    out = decide_sufficiency({"a": s(0.9, 0.9), "b": s(0.1, 0.1)})
    assert out["included"] == ["a"]
