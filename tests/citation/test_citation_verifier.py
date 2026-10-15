"""T7 — split_claims murni + keempat tindakan verdict dengan fake jev."""
from flowdesk.rag.citation_verifier import split_claims, verify_citations


def test_split_claims_sentence_and_citations():
    ans = "Pro mendukung webhook [1][2]. Enterprise 300 rpm [3].\n\nKalimat tanpa sitasi."
    claims = split_claims(ans)
    assert claims[0] == ("Pro mendukung webhook [1][2].", [1, 2])
    assert claims[1][1] == [3]
    assert len(claims) == 2                     # kalimat tanpa sitasi diabaikan


class FakeJev:
    """'SPAM' di passage -> says_nothing; 'LAWAN' -> contradicts; else supports."""
    def verify_claims(self, passage, questions):
        class A:
            def __init__(s, choice, conf): s.choice, s.confidence = choice, conf
        if "SPAM" in passage:
            return {k: A("says_nothing", 0.95) for k in questions}
        if "LAWAN" in passage:
            return {k: A("contradicts", 0.9) for k in questions}
        return {k: A("supports", 0.95) for k in questions}


def _sources(*idx):
    return [{"index": i, "document": f"d{i}", "page": None, "chunk_id": f"c{i}"}
            for i in idx]


def test_says_nothing_drops_marker():
    ans = "Klaim bagus [1]."
    check = verify_citations(FakeJev(), ans, _sources(1), {1: "teks SPAM saja"})
    assert check.dropped_markers == 1
    assert check.verified_answer == "Klaim bagus."


def test_supports_kept_and_contradicts_flags():
    check = verify_citations(FakeJev(), "Klaim A [1]. Klaim B [2].",
                             _sources(1, 2), {1: "teks wajar", 2: "teks LAWAN"})
    assert check.contradicted and "Klaim B" in check.contradicted[0]
    assert "Klaim A [1]" in check.verified_answer   # supports tidak diubah


def test_low_confidence_needs_review_only():
    class Low(FakeJev):
        def verify_claims(self, passage, questions):
            class A:
                choice, confidence = "says_nothing", 0.5
            return {k: A() for k in questions}
    check = verify_citations(Low(), "Klaim [1].", _sources(1), {1: "teks"})
    assert check.dropped_markers == 0                # conf < 0.8: dibiarkan
    assert check.needs_review


def test_unknown_index_skipped_safely():
    check = verify_citations(FakeJev(), "Klaim [9].", _sources(), {})
    assert check.checked == 0 and check.verified_answer == "Klaim [9]."

def test_multiple_markers_in_one_sentence_all_checked():
    """Regresi B1: kalimat dengan >1 marker — SEMUA marker diverifikasi.
    Bug lama: setelah marker pertama dibuang, pencarian verdict marker
    berikutnya memakai kalimat yang sudah berubah -> tidak ketemu -> spam lolos."""
    class Mixed(FakeJev):
        def verify_claims(self, passage, questions):
            class A:
                def __init__(s, c): s.choice, s.confidence = c, 0.9
            verdict = "says_nothing" if "SPAM" in passage else "supports"
            return {k: A(verdict) for k in questions}

    check = verify_citations(Mixed(), "Pro mendukung webhook [1][2][3].",
                             _sources(1, 2, 3),
                             {1: "teks SPAM", 2: "teks SPAM", 3: "teks wajar"})
    assert check.dropped_markers == 2              # [1] DAN [2] dibuang, bukan cuma [1]
    assert check.verified_answer == "Pro mendukung webhook [3]."
    assert check.checked == 3                      # ketiganya benar-benar diverifikasi



def test_contradicts_on_second_marker_is_caught():
    """Regresi B1 (kasus berbahaya): contradicts di marker KEDUA tidak
    boleh terlewat hanya karena marker pertama sudah diproses."""
    class SecondContradicts(FakeJev):
        def verify_claims(self, passage, questions):
            class A:
                def __init__(s, c): s.choice, s.confidence = c, 0.9
            return {k: A("contradicts") for k in questions}

    check = verify_citations(SecondContradicts(), "Harga Pro $49 [1][2].",
                             _sources(1, 2), {1: "teks a", 2: "teks b"})
    assert len(check.contradicted) == 2            # [1] DAN [2] keduanya tertangkap
