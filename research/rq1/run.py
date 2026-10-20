from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / 'research/rq1/results'


# Include unreachable participants so the distribution describes the whole Trivago network.
def compute_ranges(minimal_distances, name, normalize):
    c = minimal_distances.groupby(level=0, observed=False).shortest.count()
    if normalize:
        num_participants = minimal_distances.index.get_level_values(0).categories.size
        c = (c / num_participants).round(decimals=2)
    cc = c.value_counts(normalize=True).sort_index()
    if normalize:
        index = np.arange(0, cc.index.max() + 0.001, step=0.01)
        s = cc.reindex(index, fill_value=0, tolerance=0.001, method='nearest')
    else:
        index = np.arange(0, cc.index.max() + 1, step=1, dtype=np.int64)
        s = cc.reindex(index, fill_value=0)
    s.index.rename('range', inplace=True)
    return s.sort_index().cumsum().rename(name)


# Recompute distances so the results cannot silently depend on stale intermediate files.
def main():
    subprocess.run(
        [sys.executable, '-m', 'simulation.run', '--select', 'trivago'],
        cwd=ROOT,
        check=True,
    )

    trivago = pd.read_pickle(ROOT / 'data/minimal_distances/trivago.pickle.bz2')
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    for normalize, output in (
        (True, 'normalized_ranges.csv'),
        (False, 'ranges.csv'),
    ):
        ranges = compute_ranges(trivago, 'Trivago', normalize)
        ranges.to_frame().to_csv(RESULTS_PATH / output, index_label='index', float_format='%g')

    print(f'Processed {len(trivago.index.get_level_values(0).categories)} Trivago participants.')
    print(f'Range distributions written to {RESULTS_PATH.relative_to(ROOT)}.')


if __name__ == '__main__':
    main()
