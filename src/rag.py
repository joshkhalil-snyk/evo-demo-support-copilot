"""Knowledge base retrieval over resolved tickets and runbooks."""

import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from .models import EMBEDDING_MODEL

COLLECTION = "support-kb"


def embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def vector_store() -> Chroma:
    client = chromadb.PersistentClient(path="./.chroma")
    return Chroma(
        client=client,
        collection_name=COLLECTION,
        embedding_function=embeddings(),
    )


def retriever(k: int = 8):
    return vector_store().as_retriever(search_kwargs={"k": k})
