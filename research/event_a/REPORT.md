# Event A (G27 / P28)

## Baseline

M2 (`da17616`, `M2_REPRO`): all of Trivago, 364 people, 2,442 reviews. Max coverage 0.85, median 0.73.

## Material

The Spotify network: 1,730 people and 22,504 reviews, 3 Feb – 1 Mar 2020. We split it by review end time into early (3–16 Feb) and late (17 Feb – 1 Mar).

M2 didn't use Spotify, but the authors' full-month Spotify results were already in `reports/`. The early/late turnover comparison is the new part.


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

## Event B (P28)

**Frozen Week 9 decision:** We kept the authors' review-end-time model. Alternatives were to use review start/end times or individual comment/approval times; those could capture overlap better, but still require assumptions and/or more detailed data. Keeping review end times preserves comparability with RQ1 and Event A. We retain timing as a limitation; the evidence and decision are recorded in the tracker.

**Pre-Event-B prediction:** The tracker predicted that a newcomer switching the analysis from Trivago to Spotify would find the available datasets and code comments sufficient, without needing a structural redesign. This prediction was recorded before the response and is left unchanged.

**Responses and trade-off:** Leave the structure as-is and rely on the current code, or add a general dataset-selection interface. The first avoids unnecessary abstraction; the second makes dataset changes more explicit but adds indirection. We kept the structure and added one local comment at the Spotify network load to flag that the date window must change with the dataset. This small, behavior-neutral clarification avoids a larger refactor. Comments can still become stale.

**Before/after evidence and conclusion:** Before the dataset-switch exercise, `main` loaded Spotify directly, while the review-window dates were defined separately near the top of `run.py`. Its only source change was one comment at that load site; no logic, dependencies, tests, or results changed. The tracker records a newcomer-perspective walkthrough and confirms the datasets are present. This is code-walkthrough evidence, not an independent newcomer study or a build/test comparison. The Week 9 decision to avoid structural change is **supported for that maintenance task**: the dataset switch needs no new architecture, and the comment makes the date-window dependency easier to spot. The review-timing limitation remains.

### Additional Event B exercise: moving the split cutoff

**Pre-change prediction (recorded in the tracker):** A newcomer asked to move `SPLIT` from 17 to 18 February should need to change only the split constant. The main risk is the `[start, end)` boundary rule: reviews on 17 February should move from late to early without a gap or duplicate. The full `[START, END)` period and review-end-time model should remain unchanged. We did not predict whether median coverage would rise or fall because that depends on the reassigned reviews.

**Responses considered:** Make the constant change without a test (smallest edit, but leaves boundary behavior implicit); add a focused boundary test (chosen, documents the existing contract); or add a general configurable-window framework (more flexible, but unnecessary for this one cutoff).

**Response and evidence:** We left the production cutoff and analysis outputs unchanged and added `test/test_event_a.py`, which checks that adjacent windows include the start, assign the split-time review to the late window only, exclude the overall end, and have no overlap. The test passed. A data-only Spotify check simulating the one-day shift moved 973 reviews from late to early: early/late counts changed from 9,703/12,801 to 10,676/11,828, while the full review period was preserved. We did not recompute coverage or overwrite result files.

**Conclusion and trade-off:** This supports the Week 9 choice to keep the original timing model and avoid a broader redesign for a localized cutoff change. The test makes the boundary rule easier to verify, but does not establish that a different split is scientifically preferable or predict its coverage effect. The added test is a small ongoing maintenance cost.

## Run

```bash
python -m research.event_a.run
```

Writes `normalized_ranges.csv`, `ranges.csv` and `turnover.csv` to `research/event_a/results/`.
