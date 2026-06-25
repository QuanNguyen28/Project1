from embeddings.utils.chunker import split_markdown


def test_split_markdown_respects_size_and_content():
    markdown = "# Role\n\n" + ("Build reliable APIs and document trade-offs. " * 80)
    chunks = split_markdown(markdown, max_chars_per_chunk=500, overlap=60, min_chars=100)
    assert len(chunks) >= 2
    assert all(0 < len(chunk) <= 500 for chunk in chunks)
    assert "Build reliable APIs" in chunks[0]


def test_split_markdown_empty_input():
    assert split_markdown("") == []
