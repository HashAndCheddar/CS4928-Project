# Event A (G27 / P28)

## Baseline

M2 (`da17616`, `M2_REPRO`): all of Trivago, 364 people, 2,442 reviews. Max coverage 0.85, median 0.73.

## Material

The Spotify network: 1,730 people and 22,504 reviews, 3 Feb – 1 Mar 2020. We split it by review end time into early (3–16 Feb) and late (17 Feb – 1 Mar).

M2 didn't use Spotify, but the authors' full-month Spotify results were already in `reports/`. The early/late turnover comparison is the new part.

This isn't a fresh test. An earlier attempt recorded the predictions below on 29 Oct 2026, then ran this analysis. The outcome was known before this script was written.

## Prediction

Groups come from review activity only:

- **Continuing:** reviews in both halves
- **Left:** early half only
- **Joined:** late half only
- **Experienced:** top quarter of early reviewers

1. If experienced people leave, late median coverage is lower than early.
2. People who joined have lower late coverage than continuing people.

Coverage staying the same or rising, or newcomers matching continuing people, would challenge these.

## Results

| | Max | Median |
| --- | ---: | ---: |
| Trivago (M2) | 0.85 | 0.73 |
| Spotify, full month | 0.85 | 0.73 |
| Spotify, early | 0.65 | 0.10 |
| Spotify, late | 0.76 | 0.46 |

| Group | People | Experienced | Early median | Late median |
| --- | ---: | ---: | ---: | ---: |
| Continuing | 1,397 | 379 | 0.12 | 0.50 |
| Left | 131 | 3 | 0.01 | – |
| Joined | 202 | 0 | – | 0.02 |

- **Prediction 1 is challenged.** Coverage rose from 0.10 to 0.46 although 3 experienced people left.
- **Prediction 2 is supported.** People who joined have median coverage 0.02, against 0.50 for continuing people.

## Comparison with M2

- **Transfers:** the method, and the full-month 0.85 max (Spotify's exact value is 0.8509, Trivago's 0.8516).
- **Doesn't transfer:** 85% as a fixed ceiling. Two-week windows reach only 0.65 and 0.76.
- **Limits:** only 3 experienced people left. The late half had 32% more reviews, which could explain the rise. This is activity, not real staff turnover, so we make no causal claim.

## Design implication

People who joined reach about 2% of the network through review, so review alone won't pass design knowledge to them. Applying information hiding and low coupling: keep each module's decisions behind a small, documented interface, so it can be changed with local knowledge.

## Run

```bash
python -m research.event_a.run
```

Writes `normalized_ranges.csv`, `ranges.csv` and `turnover.csv` to `research/event_a/results/`.

## Tracker text

- **J31 (add):** `Event A: research/event_a/ (REPORT.md, run.py, results/).`
- **K31:** `Spotify, early (3–16 Feb) vs late (17 Feb–1 Mar 2020), same M2 method. Predict late coverage falls if experienced reviewers leave, and newcomers have lower coverage. Recorded 29 Oct 2026 before the first run.`
- **L31:** `Spotify full month max 0.85, as in M2. Median rose 0.10→0.46 despite 3 experienced leaving: prediction 1 challenged. Newcomers 0.02 vs continuing 0.50: prediction 2 supported. 85% depends on the window length.`
