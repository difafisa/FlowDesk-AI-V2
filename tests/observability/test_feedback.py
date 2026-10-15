"""Phase 6 T3 — test feedback store (fake conn + fake langfuse, tanpa jaringan)."""
from flowdesk.observability.feedback import FeedbackStore


class FakeCursor:
    def __init__(self, store):
        self.store = store
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False
    def execute(self, sql, params=None):
        self.store.executed.append((sql, params))
        if sql.startswith("SELECT rating"):
            self.store.select_result = [("helpful", 3), ("nothelpful", 1)]
        elif sql.startswith("SELECT run_id"):
            self.store.select_result = [("r1", "helpful", None, "t")]
    def fetchall(self):
        return self.store.select_result


class FakeConn:
    """Rekam SQL; table feedback disimulasikan lewat list."""
    def __init__(self):
        self.executed = []
        self.select_result = []
        self.cursor = lambda: FakeCursor(self)
        self.commits = 0
    def execute(self, sql):
        self.executed.append((sql, None))
    def commit(self):
        self.commits += 1


class FakeLangfuse:
    def __init__(self):
        self.scores = []
        self.flushed = 0
    def create_score(self, **kw):
        self.scores.append(kw)
    def flush(self):
        self.flushed += 1


def make_store(langfuse=None, conn=None):
    conn = conn or FakeConn()
    return FeedbackStore(conn=conn, langfuse=langfuse), conn


# --- simpan + round-trip -------------------------------------------------

def test_submit_helpful_menyimpan_dan_mengirim_score():
    lf = FakeLangfuse()
    store, conn = make_store(langfuse=lf)
    ok = store.submit("trace-1", helpful=True, comment="jelas dan ringkas")

    assert ok is True
    sql, params = conn.executed[-1]
    assert "INSERT INTO feedback" in sql
    assert params == ("trace-1", "helpful", "jelas dan ringkas")
    # score Langfuse terkirim ke trace yang sama
    assert len(lf.scores) == 1
    s = lf.scores[0]
    assert s["trace_id"] == "trace-1"
    assert s["name"] == "user_feedback"
    assert s["value"] == 1.0
    assert lf.flushed == 1


def test_submit_nothelpful_nilai_nol():
    lf = FakeLangfuse()
    store, _ = make_store(langfuse=lf)
    store.submit("trace-2", helpful=False)
    assert lf.scores[0]["value"] == 0.0


def test_tanpa_langfuse_tetap_tersimpan():
    store, conn = make_store(langfuse=None)
    assert store.submit("trace-3", helpful=True) is True
    assert any("INSERT INTO feedback" in sql for sql, _ in conn.executed)


# --- fail-safe -------------------------------------------------------------

def test_db_error_tidak_melempar():
    class BoomConn(FakeConn):
        def __init__(self):
            super().__init__()
            # atribut instance menimpa method class — override di level sama
            def boom():
                raise RuntimeError("db down")
            self.cursor = boom
    store = FeedbackStore(conn=BoomConn(), langfuse=None)
    assert store.submit("t", helpful=True) is False   # tidak raise


def test_langfuse_error_tidak_menggagalkan_penyimpanan():
    class BoomLF:
        def create_score(self, **kw):
            raise RuntimeError("langfuse down")
        def flush(self):
            pass
    store, conn = make_store(langfuse=BoomLF())
    assert store.submit("trace-4", helpful=True) is True  # tetap tersimpan
    assert any("INSERT INTO feedback" in sql for sql, _ in conn.executed)


def test_tanpa_run_id_tidak_kirim_score():
    lf = FakeLangfuse()
    store, _ = make_store(langfuse=lf)
    store.submit(None, helpful=True)
    assert lf.scores == []          # tak ada trace yang bisa dituju


def test_summary_bentuknya_benar():
    store, _ = make_store()
    s = store.summary()
    assert s["helpful"] == 3 and s["nothelpful"] == 1
    assert len(s["recent"]) == 1
