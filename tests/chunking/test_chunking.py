from flowdesk.chunking.structure_chunker import CHUNK_SIZE
from flowdesk.chunking.structure_chunker import chunk_markdown, _approx_tokens

SAMPLE = """# API Documentation
## Authentication
### Using the API Key
API key is sent via the Authorization header. """ + ("Details follow. " * 200)

def test_small_section_is_single_chunk():
    """PRD 2.5 contoh 1: bagian 150 token = 1 chunk, tidak dipaksa 700."""
    chunks = chunk_markdown("# T\n## S\n" + "Short paragraph. ", "t.md")
    assert len(chunks) == 1
    assert _approx_tokens(chunks[0].content) < 700

def test_metadata_populated():
    chunks = chunk_markdown(SAMPLE, "api.md")
    c = chunks[0]
    assert c.document == "api.md"
    assert c.section == "API Documentation"
    assert c.subsection == "Authentication"
    assert c.source_type == "markdown"
    assert c.chunk_id

def test_chunks_end_at_sentence_boundary():
    """PRD 2.4: split terjadi di boundary kalimat, bukan tengah kata."""
    for c in chunk_markdown(SAMPLE, "api.md"):
        body = c.content.split("\n\n")[-1].rstrip()
        if len(body) >= CHUNK_SIZE:
            assert body[-1] in ".!?:" or body[-1] == "`", f"potong di tengah: ...{body[-40:]!r}"
