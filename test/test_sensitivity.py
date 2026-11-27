import random
import unittest
from datetime import datetime, timedelta

from research.sensitivity.timing import RULES, reach
from simulation.minimal_distances import DistanceType, single_source_dijkstra_hyperedges
from simulation.model import CommunicationNetwork


def random_channels(seed, people=12, reviews=30):
    rng = random.Random(seed)
    names = [f'p{i:02d}' for i in range(people)]
    channels = {}
    for r in range(reviews):
        # Few distinct hours, so equal and overlapping times are common.
        start = datetime(2020, 1, 1) + timedelta(hours=rng.randint(0, 8))
        end = start + timedelta(hours=rng.randint(0, 4))
        channels[f'r{r:03d}'] = (start, end, frozenset(rng.sample(names, rng.randint(2, 4))))
    return channels


class TimingRuleTest(unittest.TestCase):
    def test_paper_rule_matches_authors_algorithm(self):
        for seed in range(25):
            channels = random_channels(seed)
            network = CommunicationNetwork(
                {c: set(m) for c, (_, _, m) in channels.items()},
                {c: end for c, (_, end, _) in channels.items()},
            )
            reached = reach(channels, RULES['paper'])
            for source in network.participants():
                expected = set(single_source_dijkstra_hyperedges(network, source, DistanceType.SHORTEST))
                self.assertEqual(reached[source], expected, f'seed {seed}, source {source}')

    def test_rules_are_nested(self):
        for seed in range(25):
            channels = random_channels(seed)
            strict, paper, overlap = (reach(channels, RULES[r]) for r in ('closed_first', 'paper', 'overlap'))
            for p in paper:
                self.assertLessEqual(strict[p], paper[p])
                self.assertLessEqual(paper[p], overlap[p])


if __name__ == '__main__':
    unittest.main()
