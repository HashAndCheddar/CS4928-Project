from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
import math

import pandas as pd

from research.rq1.run import compute_ranges
from simulation.minimal_distances import single_source_dijkstra_hyperedges, DistanceType
from simulation.model import CommunicationNetwork

ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / 'research/event_a/results'

START = datetime(2020, 2, 3)
SPLIT = datetime(2020, 2, 17)
END = datetime(2020, 3, 2)


# Keep only the reviews that ended between start and end.
def select_reviews(network, start, end):
    channels = {}
    timings = {}

    for channel in network.channels():
        if start <= network.timings(channel) < end:
            channels[channel] = network.participants(channel)
            timings[channel] = network.timings(channel)

    return CommunicationNetwork(channels, timings)


# Build the same distance table as simulation/run.py, so compute_ranges can be reused.
def compute_minimal_distances(network):
    participants = tuple(sorted(network.participants()))
    category = pd.api.types.CategoricalDtype(categories=participants, ordered=False)

    min_distances = []
    with ProcessPoolExecutor() as executor:
        futures = {}
        for p in participants:
            future = executor.submit(
                single_source_dijkstra_hyperedges,
                network,
                p,
                DistanceType.SHORTEST,
            )
            futures[future] = p

        for future, source in futures.items():
            for target, distance in future.result().items():
                min_distances += [(source, target, distance)]

    min_distances_df = pd.DataFrame(min_distances, columns=['source', 'target', 'shortest'])
    min_distances_df.source = min_distances_df.source.astype(category)
    min_distances_df.target = min_distances_df.target.astype(category)
    return min_distances_df.set_index(['source', 'target'])


# Normalized range per participant, rounded the same way as compute_ranges.
def compute_coverage(minimal_distances):
    c = minimal_distances.groupby(level=0, observed=False).shortest.count()
    return (c / c.size).round(decimals=2)


# The top quarter of participants by number of reviews, ties broken by participant id.
def find_experienced(network):
    reviews = []
    for channel in network.channels():
        reviews += network.participants(channel)

    counts = pd.Series(reviews).value_counts().sort_index()
    counts = counts.sort_values(ascending=False, kind='stable')
    return counts.index[:math.ceil(counts.size / 4)]


def main():
    spotify = CommunicationNetwork.from_json(ROOT / 'data/networks/spotify.json.bz2')
    early = select_reviews(spotify, START, SPLIT)
    late = select_reviews(spotify, SPLIT, END)

    spotify_distances = compute_minimal_distances(spotify)
    early_distances = compute_minimal_distances(early)
    late_distances = compute_minimal_distances(late)

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    for normalize, output in (
        (True, 'normalized_ranges.csv'),
        (False, 'ranges.csv'),
    ):
        ranges = pd.concat([
            compute_ranges(spotify_distances, 'Spotify', normalize),
            compute_ranges(early_distances, 'Early', normalize),
            compute_ranges(late_distances, 'Late', normalize),
        ], axis=1)
        ranges.fillna(1).to_csv(RESULTS_PATH / output, index_label='index', float_format='%g')

    # Turnover is based on review activity only: who reviews early, late, or in both halves.
    early_coverage = compute_coverage(early_distances)
    late_coverage = compute_coverage(late_distances)
    experienced = find_experienced(early)

    cohorts = {
        'all': early_coverage.index.union(late_coverage.index),
        'continuing': early_coverage.index.intersection(late_coverage.index),
        'left': early_coverage.index.difference(late_coverage.index),
        'joined': late_coverage.index.difference(early_coverage.index),
    }

    rows = []
    for cohort, people in cohorts.items():
        rows.append({
            'cohort': cohort,
            'participants': len(people),
            'experienced': people.isin(experienced).sum(),
            'early_median': early_coverage.reindex(people).median(),
            'late_median': late_coverage.reindex(people).median(),
        })

    turnover = pd.DataFrame(rows).set_index('cohort')
    turnover.to_csv(RESULTS_PATH / 'turnover.csv', float_format='%g')

    print(turnover.to_string())
    print(f'Results written to {RESULTS_PATH.relative_to(ROOT)}.')


if __name__ == '__main__':
    main()
