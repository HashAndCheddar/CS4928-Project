"""Timing-model sensitivity for the Week 9 design decision (Trivago).

The paper lets information pass from review A into review B when A ends before B ends.
The data also records when each review started, so the two alternatives we rejected in
Week 9 can be measured as bounds around that rule:

    closed_first : A.end   < B.start  (B must open after A has closed; strictest)
    paper        : A.end   < B.end    (the authors' rule, unchanged)
    overlap      : A.start < B.end    (any overlap counts; most permissive)

Each rule is a subset of the next, so coverage can only grow from left to right.

    python -m research.sensitivity.timing
"""
import bz2
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'research/sensitivity/results'
RQ1_DISTANCES = ROOT / 'data/minimal_distances/trivago.pickle.bz2'

RULES = {
    'closed_first': lambda a, b: a[1] < b[0],
    'paper': lambda a, b: a[1] < b[1],
    'overlap': lambda a, b: a[0] < b[1],
}


def load(path):
    raw = json.loads(bz2.decompress(path.read_bytes()))
    return {
        str(c): (datetime.fromisoformat(r['start']), datetime.fromisoformat(r['end']), frozenset(r['participants']))
        for c, r in raw.items()
    }


def reach(channels, rule):
    """For every participant, the set of other participants their information can reach.

    Like the authors' algorithm, every review the source takes part in is reached
    regardless of time; onward steps must satisfy `rule(earlier, later)`.
    """
    by_participant = defaultdict(list)
    for c, (_, _, members) in channels.items():
        for p in members:
            by_participant[p].append(c)

    reached = {}
    for source, own in by_participant.items():
        seen = set(own)
        queue = list(own)
        while queue:
            a = queue.pop()
            for p in channels[a][2]:
                for b in by_participant[p]:
                    if b not in seen and rule(channels[a], channels[b]):
                        seen.add(b)
                        queue.append(b)
        reached[source] = set().union(*(channels[c][2] for c in seen)) - {source}
    return reached


def main():
    channels = load(ROOT / 'data/networks/trivago.json.bz2')
    participants = sorted({p for _, _, members in channels.values() for p in members})
    n = len(participants)

    coverage = pd.DataFrame({
        name: pd.Series({p: len(r) / n for p, r in reach(channels, rule).items()})
        for name, rule in RULES.items()
    }).loc[participants]
    coverage.index.name = 'participant'

    # The paper rule must give exactly the RQ1 reach counts; otherwise the comparison is meaningless.
    rq1 = pd.read_pickle(RQ1_DISTANCES).groupby(level=0, observed=False).shortest.count()
    if not (coverage['paper'] * n).round().astype(int).equals(rq1.loc[participants].astype(int).rename('paper')):
        raise SystemExit('Paper rule does not reproduce the RQ1 per-participant reach counts')
    print('Paper rule reproduces the RQ1 reach count for all participants.')

    # Max/median/mean only: the overlap distribution is nearly two-valued, so the paper's
    # percentile rows would be misleading for it.
    summary = pd.DataFrame({
        'max': coverage.max(),
        'median': coverage.median(),
        'mean': coverage.mean(),
        'participants_changed_vs_paper': coverage.ne(coverage['paper'], axis=0).sum(),
    })
    summary.index.name = 'rule'

    RESULTS.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(RESULTS / 'timing_coverage.csv', float_format='%g')
    summary.to_csv(RESULTS / 'timing_summary.csv', float_format='%.4g')
    print(summary.round(2).to_string())


if __name__ == '__main__':
    main()
