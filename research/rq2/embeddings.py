"""Text embeddings for retrieval: OpenRouter (cached on disk) or a local TF-IDF fallback.

Both return L2-normalised rows, so a dot product is cosine similarity.
"""
import hashlib
import re

import numpy as np


def normalise(vectors):
    vectors = np.asarray(vectors, dtype=np.float64)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(norms == 0, 1, norms)


def tfidf(texts):
    """Smoothed TF-IDF (same formula as scikit-learn's default), fitted on all texts given."""
    tokens = [re.findall(r'[a-z0-9]+', text.lower()) for text in texts]
    vocabulary = {word: i for i, word in enumerate(sorted({w for ts in tokens for w in ts}))}
    counts = np.zeros((len(texts), len(vocabulary)))
    for row, ts in enumerate(tokens):
        for word in ts:
            counts[row, vocabulary[word]] += 1
    document_frequency = (counts > 0).sum(axis=0)
    idf = np.log((1 + len(texts)) / (1 + document_frequency)) + 1
    return normalise(counts * idf)


def openrouter(texts, client, model, dimensions, cache_path, batch_size=100):
    """Embed texts through OpenRouter, only requesting texts missing from the .npz cache."""
    keys = [hashlib.sha256(f'{model}|{dimensions}|{t}'.encode()).hexdigest() for t in texts]
    cache = {}
    if cache_path.exists():
        with np.load(cache_path) as stored:
            cache = dict(zip(stored['keys'], stored['vectors']))

    missing = [i for i, key in enumerate(keys) if key not in cache]
    if missing and client is None:
        raise RuntimeError(f'{len(missing)} embeddings are not cached and no OPENROUTER_API_KEY is set')
    for start in range(0, len(missing), batch_size):
        batch = missing[start:start + batch_size]
        data = client.post('/embeddings', {
            'model': model,
            'input': [texts[i] for i in batch],
            'dimensions': dimensions,
        })['data']
        vectors = [row['embedding'] for row in sorted(data, key=lambda row: row['index'])]
        if len(vectors) != len(batch) or any(len(v) != len(vectors[0]) for v in vectors):
            raise RuntimeError(f'Expected {len(batch)} equal-length embeddings, got {len(vectors)}')
        if not np.isfinite(vectors).all():
            raise RuntimeError('OpenRouter returned non-finite embedding values')
        cache.update(zip((keys[i] for i in batch), np.asarray(vectors, dtype=np.float32)))

    if missing:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_path, keys=np.array(list(cache)), vectors=np.stack(list(cache.values())))
    return normalise([cache[key] for key in keys])
