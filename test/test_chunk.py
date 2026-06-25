import os

import pytest
from dotenv import load_dotenv
from pymilvus import Collection, connections, utility

load_dotenv()


@pytest.mark.integration
def test_milvus_collection_schema():
    try:
        connections.connect(
            alias="default",
            host=os.getenv("MILVUS_HOST", "localhost"),
            port=os.getenv("MILVUS_PORT", "19530"),
        )
    except Exception as exc:
        pytest.skip(f"Milvus is unavailable: {exc}")

    name = os.getenv("MILVUS_COLLECTION", "jdchunks")
    if not utility.has_collection(name):
        pytest.skip(f"Milvus collection {name!r} has not been created")

    collection = Collection(name)
    fields = {field.name for field in collection.schema.fields}
    assert {"chunk_id", "jd_id", "chunk_index", "object_url", "embedding"} <= fields
