import json
import random
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from research.rq2 import diffusion, embeddings, items
from research.rq2.generation import Generator, parse_cited
from simulation.minimal_distances import DistanceType, single_source_dijkstra_hyperedges
from simulation.model import CommunicationNetwork


def random_network(seed, people=12, reviews=30):
    rng = random.Random(seed)
    names = [f'p{i:02d}' for i in range(people)]
    channels, timings = {}, {}
    for r in range(reviews):
        channels[f'r{r:03d}'] = set(rng.sample(names, rng.randint(2, 4)))
        # Few distinct times, so same-time reviews are common.
        timings[f'r{r:03d}'] = datetime(2020, 1, 1) + timedelta(hours=rng.randint(0, 8))
    return CommunicationNetwork(channels, timings)


class PerfectMemoryTest(unittest.TestCase):
    def test_matches_authors_reachability(self):
        for seed in range(25):
            network = random_network(seed)
            participants, memory = diffusion.diffuse(network, diffusion.perfect)
            for s, source in enumerate(participants):
                reached = {participants[t] for t in np.flatnonzero(memory[:, s]) if t != s}
                expected = set(single_source_dijkstra_hyperedges(network, source, DistanceType.SHORTEST))
                self.assertEqual(reached, expected, f'seed {seed}, source {source}')

    def test_same_time_reviews_do_not_chain(self):
        t = datetime(2020, 1, 1)
        network = CommunicationNetwork({'r1': {'a', 'b'}, 'r2': {'b', 'c'}}, {'r1': t, 'r2': t})
        participants, memory = diffusion.diffuse(network, diffusion.perfect)
        self.assertFalse(memory[participants.index('c'), participants.index('a')])


class BoundedMemoryTest(unittest.TestCase):
    def test_top_k_breaks_ties_by_index(self):
        scores = np.array([0.5, 0.9, 0.5, 0.5])
        np.testing.assert_array_equal(diffusion.top_k(scores, np.array([0, 2, 3, 1]), 3), [1, 0, 2])

    def test_bounded_reach_never_exceeds_perfect(self):
        for seed in range(10):
            network = random_network(seed, people=20, reviews=60)
            similarity = {r: np.random.default_rng(seed).random(20) for r in network.channels()}
            _, perfect = diffusion.diffuse(network, diffusion.perfect)
            for share in (diffusion.retrieval(similarity, 2), diffusion.random_k(2, seed)):
                _, bounded = diffusion.diffuse(network, share)
                self.assertTrue((bounded <= perfect).all())

    def test_large_k_equals_perfect(self):
        network = random_network(3)
        similarity = {r: np.zeros(12) for r in network.channels()}
        _, perfect = diffusion.diffuse(network, diffusion.perfect)
        _, rag = diffusion.diffuse(network, diffusion.retrieval(similarity, 12))
        np.testing.assert_array_equal(rag, perfect)


class ItemsTest(unittest.TestCase):
    def test_items_are_distinct_and_reproducible(self):
        people = [f'p{i}' for i in range(1730)]
        texts, topics = items.make_items(people, seed=0)
        self.assertEqual(len(set(texts)), len(people))
        self.assertEqual(items.make_items(people, seed=0), (texts, topics))
        self.assertEqual(items.make_query('r1', ['caching', 'api'], 0), items.make_query('r1', ['caching', 'api'], 0))


class EmbeddingsTest(unittest.TestCase):
    def test_tfidf_rows_are_unit_length_and_related_texts_score_higher(self):
        v = embeddings.tfidf(['cache invalidation bug', 'cache invalidation fix', 'translation files'])
        np.testing.assert_allclose(np.linalg.norm(v, axis=1), 1)
        self.assertGreater(v[0] @ v[1], v[0] @ v[2])


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.calls = 0

    def post(self, path, body):
        self.calls += 1
        return {'choices': [{'message': {'content': self.content}}]}


class GenerationTest(unittest.TestCase):
    def test_parse_rejects_out_of_range_and_non_integer_citations(self):
        self.assertEqual(parse_cited('{"comment": "x", "cited": [1, 3, 9, "2", true]}', 3), ({1, 3}, 3))
        self.assertIsNone(parse_cited('no json here', 3))

    def test_only_offered_cited_items_pass_and_responses_are_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'generation.jsonl'
            client = FakeClient(json.dumps({'comment': 'ok', 'cited': [2, 7]}))
            texts = ['a', 'b', 'c', 'd', 'e']
            cited = Generator(client, 'm', cache).cite('q', np.array([4, 1, 3]), texts)
            np.testing.assert_array_equal(cited, [1])

            replay = Generator(None, 'm', cache)
            np.testing.assert_array_equal(replay.cite('q', np.array([4, 1, 3]), texts), [1])
            self.assertEqual((client.calls, replay.stats['cache_hits']), (1, 1))

    def test_skips_llm_when_review_cannot_change_memory(self):
        network = CommunicationNetwork({'r1': {'a', 'b'}}, {'r1': datetime(2020, 1, 1)})

        def cite(review, candidates):
            raise AssertionError('should not be called')

        _, memory = diffusion.diffuse(network, diffusion.generated(lambda r, m, mem: np.array([], dtype=int), cite))
        np.testing.assert_array_equal(memory, np.eye(2, dtype=bool))


if __name__ == '__main__':
    unittest.main()
