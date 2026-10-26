"""Loads knowledge base articles and cached embeddings from shared storage."""

import hashlib
import pickle
import tarfile

import torch
import yaml
from pypdf import PdfReader

from .models import SELF_HOSTED_EMBEDDING_MODEL


def load_article_manifest(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=yaml.Loader)


def load_cached_embeddings(path: str):
    with open(path, "rb") as fh:
        return pickle.load(fh)


def load_reranker_weights(path: str):
    return torch.load(path)


def unpack_article_bundle(archive: str, dest: str) -> None:
    with tarfile.open(archive) as tar:
        tar.extractall(dest)


def pdf_text(path: str) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def self_hosted_embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(SELF_HOSTED_EMBEDDING_MODEL, trust_remote_code=True)
