from flowdesk.rag.output_validator import looks_truncated


def test_truncated_mid_word():
    assert looks_truncated("Paket Pro (Enterprise juga mendukung). Pel") is True


def test_normal_answer_not_truncated():
    assert looks_truncated("Rate limit API Pro adalah 60 request per menit [1].") is False


def test_ends_with_citation_not_truncated():
    assert looks_truncated("...hanya tersedia di paket Pro dan Enterprise [1][2].") is False


def test_empty_is_not_truncated():
    assert looks_truncated("") is False
    assert looks_truncated(None or "") is False
