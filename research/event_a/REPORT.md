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

## Maintenance checks on the Event A analysis

*These were originally recorded as Event B. Event B is now the RQ2 retrieval-augmented memory extension; see [`research/rq2/REPORT.md`](../rq2/REPORT.md). The checks below are kept unchanged as robustness checks of the Week 9 timing decision and the Event A split.*

**Frozen Week 9 decision:** We kept the authors' review-end-time model. Alternatives were to use review start/end times or individual comment/approval times; those could capture overlap better, but still require assumptions and/or more detailed data. Keeping review end times preserves comparability with RQ1 and Event A. We retain timing as a limitation; the evidence and decision are recorded in the tracker.

**Prediction (recorded before the change):** The tracker predicted that a newcomer switching the analysis from Trivago to Spotify would find the available datasets and code comments sufficient, without needing a structural redesign. This prediction was recorded before the response and is left unchanged.

**Responses and trade-off:** Leave the structure as-is and rely on the current code, or add a general dataset-selection interface. The first avoids unnecessary abstraction; the second makes dataset changes more explicit but adds indirection. We kept the structure and added one local comment at the Spotify network load to flag that the date window must change with the dataset. This small, behavior-neutral clarification avoids a larger refactor. Comments can still become stale.

**Before/after evidence and conclusion:** Before the dataset-switch exercise, `main` loaded Spotify directly, while the review-window dates were defined separately near the top of `run.py`. Its only source change was one comment at that load site; no logic, dependencies, tests, or results changed. The tracker records a newcomer-perspective walkthrough and confirms the datasets are present. This is code-walkthrough evidence, not an independent newcomer study or a build/test comparison. The Week 9 decision to avoid structural change is **supported for that maintenance task**: the dataset switch needs no new architecture, and the comment makes the date-window dependency easier to spot. The review-timing limitation remains.

### Moving the split cutoff

**Pre-change prediction (recorded in the tracker):** A newcomer asked to move `SPLIT` from 17 to 18 February should need to change only the split constant. The main risk is the `[start, end)` boundary rule: reviews on 17 February should move from late to early without a gap or duplicate. The full `[START, END)` period and review-end-time model should remain unchanged. We did not predict whether median coverage would rise or fall because that depends on the reassigned reviews.

**Responses considered:** Make the constant change without a test (smallest edit, but leaves boundary behavior implicit); add a focused boundary test (chosen, documents the existing contract); or add a general configurable-window framework (more flexible, but unnecessary for this one cutoff).

**Response and evidence:** We left the production cutoff unchanged and added `test/test_event_a.py`, which checks that adjacent windows include the start, assign the split-time review to the late window only, exclude the overall end, and have no overlap. The test passed. A data-only sensitivity check evaluated splits on 16–19 February without recomputing distances or coverage. Every split preserved the same 22,504 reviews, but the activity cohorts changed with the cutoff:

| Split date | Early/late reviews | Early/late participants | Continuing | Left | Joined |
| --- | ---: | ---: | ---: | ---: | ---: |
| 16 Feb | 9,671 / 12,833 | 1,528 / 1,599 | 1,397 | 131 | 202 |
| 17 Feb (original) | 9,703 / 12,801 | 1,528 / 1,599 | 1,397 | 131 | 202 |
| 18 Feb | 10,676 / 11,828 | 1,547 / 1,585 | 1,402 | 145 | 183 |
| 19 Feb | 11,776 / 10,728 | 1,587 / 1,560 | 1,417 | 170 | 143 |

Moving the cutoff from 17 to 18 February reassigns 973 reviews and changes the cohort sizes, even though the full period is unchanged. The counts are saved in [`split_sensitivity.csv`](./results/split_sensitivity.csv). No Event A output files were overwritten.

**Conclusion and trade-off:** The focused test supports keeping the existing window-selection structure rather than adding a general framework. The sensitivity check also shows that turnover cohort sizes depend on the chosen cutoff, so the Event A interpretation should not be treated as split-independent. This does not establish that another cutoff is scientifically preferable; coverage was not recomputed. The added test is a small ongoing maintenance cost.

## Run

```bash
python -m research.event_a.run
```

Writes `normalized_ranges.csv`, `ranges.csv` and `turnover.csv` to `research/event_a/results/`.
