"""Item-level information diffusion with bounded memory (RQ2).

Each participant starts with one information item: their own. Reviews are processed
in end-time order, and a review passes the items its members share to every member.
Reviews that end at the same instant all see the memory as it was just before that
instant. This is the strict `earlier end < later end` rule in
simulation/minimal_distances.py. With perfect memory, the item reach therefore equals
the authors' range.

A `share(review, members, memory)` function decides which items a review passes on.
Memory is a boolean matrix: memory[holder, item]. Nothing is ever forgotten. The memory
limit is on what a participant can *retrieve* into a review.
"""
from itertools import groupby
import zlib

import numpy as np
import pandas as pd


def diffuse(network, share):
    participants = tuple(sorted(network.participants()))
    index = {p: i for i, p in enumerate(participants)}
    memory = np.eye(len(participants), dtype=bool)

    reviews = sorted(network.channels(), key=lambda c: (network.timings(c), c))
    for _, same_time in groupby(reviews, key=network.timings):
        updates = []
        for review in same_time:
            members = sorted(index[p] for p in network.participants(review))
            updates.append((members, share(review, members, memory)))
        # Apply after the whole group so same-time reviews cannot chain.
        for members, shared in updates:
            memory[np.ix_(members, shared)] = True
    return participants, memory


def perfect(review, members, memory):
    return np.flatnonzero(memory[members].any(axis=0))


# Highest score first; equal scores go to the lower item index so runs are repeatable.
def top_k(scores, candidates, k):
    order = np.lexsort((candidates, -scores[candidates]))
    return candidates[order[:k]]


def retrieval(similarity, k):
    """RAG memory: each member retrieves its k known items most similar to the review query.

    `similarity` maps a review id to a score for every item.
    """
    def share(review, members, memory):
        scores = similarity[review]
        picked = [top_k(scores, np.flatnonzero(memory[m]), k) for m in members]
        return np.unique(np.concatenate(picked))
    return share


def random_k(k, seed):
    """Control: each member shares k known items chosen at random (seeded per review and member)."""
    def share(review, members, memory):
        picked = []
        for m in members:
            known = np.flatnonzero(memory[m])
            rng = np.random.default_rng([seed, zlib.crc32(review.encode()), m])
            picked.append(rng.choice(known, size=min(k, known.size), replace=False))
        return np.unique(np.concatenate(picked))
    return share


def generated(retrieve, cite):
    """RAG with generation: retrieved items are offered to an LLM; only the ones it cites are shared.

    `cite(review, candidates)` returns the validated subset of candidates. It is skipped when
    every member already holds every candidate, because the review could not change memory.
    """
    def share(review, members, memory):
        candidates = retrieve(review, members, memory)
        if memory[np.ix_(members, candidates)].all():
            return candidates
        return cite(review, candidates)
    return share


def to_minimal_distances(participants, memory):
    """Reachability in the shape simulation/run.py writes, so research.rq1.run.compute_ranges applies.

    Item i belongs to participant i, so holder t having item s means s reached t.
    """
    category = pd.api.types.CategoricalDtype(categories=participants, ordered=False)
    targets, sources = np.nonzero(memory)
    keep = targets != sources
    frame = pd.DataFrame({
        'source': pd.Categorical.from_codes(sources[keep], dtype=category),
        'target': pd.Categorical.from_codes(targets[keep], dtype=category),
        'shortest': 1,
    })
    return frame.set_index(['source', 'target'])


# Fraction of the network each item reached, excluding its owner (as RQ1 normalizes range).
def coverage(participants, memory):
    reached = memory.sum(axis=0) - 1
    return pd.Series(reached / len(participants), index=list(participants), name='coverage')
