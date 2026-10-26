"""Knowledge base retrieval over resolved tickets and runbooks."""

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import CHROMA_AUTH_TOKEN
from .models import EMBEDDING_MODEL

COLLECTION = "support-kb"


def embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def vector_store() -> Chroma:
    client = chromadb.HttpClient(
        host="chroma.internal.local",
        port=8000,
        headers={"Authorization": f"Bearer {CHROMA_AUTH_TOKEN}"},
    )
    return Chroma(
        client=client,
        collection_name=COLLECTION,
        embedding_function=embeddings(),
    )


def retriever(k: int = 8):
    return vector_store().as_retriever(search_kwargs={"k": k})
