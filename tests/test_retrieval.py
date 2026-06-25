import pytest

from src.services.retriever_service import retrieve_hybrid


@pytest.mark.integration
def test_lexical_retrieval_is_diverse_and_relevant():
    results = retrieve_hybrid(
        "sales account executive",
        None,
        5,
        mode="lexical",
        max_chunks_per_jd=1,
    )
    assert len(results) == 5
    assert len({item.jd_id for item in results}) == 5
    assert all(item.retrieval_method == "lexical" for item in results)
    assert any("account" in (item.title or "").lower() for item in results)


@pytest.mark.integration
def test_retrieval_company_filter():
    results = retrieve_hybrid(
        "product design collaboration",
        None,
        5,
        mode="lexical",
        company="Figma",
        max_chunks_per_jd=1,
    )
    assert results
    assert all(item.company == "Figma" for item in results)
