import unittest
from datetime import datetime

from research.event_a.run import select_reviews
from simulation.model import CommunicationNetwork


class SelectReviewsTest(unittest.TestCase):
    def test_adjacent_windows_assign_split_review_to_late_only(self):
        start = datetime(2020, 2, 3)
        split = datetime(2020, 2, 17)
        end = datetime(2020, 3, 2)
        network = CommunicationNetwork(
            {
                'before': {'p1', 'p2'},
                'start': {'p1', 'p3'},
                'split': {'p2', 'p3'},
                'end': {'p1', 'p2'},
            },
            {
                'before': datetime(2020, 2, 2),
                'start': start,
                'split': split,
                'end': end,
            },
        )

        early = select_reviews(network, start, split)
        late = select_reviews(network, split, end)

        self.assertEqual(early.channels(), {'start'})
        self.assertEqual(late.channels(), {'split'})
        self.assertTrue(early.channels().isdisjoint(late.channels()))
        self.assertEqual(early.channels() | late.channels(), {'start', 'split'})
