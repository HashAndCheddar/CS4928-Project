# Event B: newcomer maintenance (G27 / P28)

Final-synthesis account, 20 November 2026. This document synthesizes existing maintenance work; it is not a new experiment or a new preregistration.

## Pressure and prior decision

The official P28 Event B asks whether a contributor without prior review involvement can maintain the area using the M4 artefact/design, and what knowledge remains implicit. RQ2's retrieval experiment is reported separately in [research/rq2/REPORT.md](../rq2/REPORT.md).

The recorded Week 9 decision was to keep the authors' review-end-time model for comparability with RQ1 and Event A. Start/end intervals and comment/approval timestamps were alternatives, but require further modelling assumptions or data. The current evidence does not validate an alternative timing model.

The maintenance response is [c936f52](https://github.com/HashAndCheddar/CS4928-Project/commit/c936f52cc02d0e0b5f2d70d87df29ea71233195a), compared with its parent [a3704ea](https://github.com/HashAndCheddar/CS4928-Project/commit/a3704ea1b5cf30a513b0e945af55613de8c248a7). Its historical account records the expectation that the available datasets and code would support a local change without structural redesign. The exact relation of the parent to the actual M4 freeze, and independent evidence for the prediction's recording time, still require confirmation from the group's original records.

## Maintenance account and alternatives

The team reports retrospectively that the maintenance contributor found the code and repository reports readable enough to follow the work. They did not retain contemporaneous walkthrough notes or timings. This is a qualitative team account, not a measured newcomer experiment.

The recorded alternatives were:

1. Retain the structure and rely on the existing code. This adds no abstraction, but the dataset/date dependency and half-open window rule remain implicit.
2. Retain the structure with a local clarification and boundary test. This exposes the relevant dependency and makes selection behaviour executable with a small maintenance cost.
3. Add a general dataset/window configuration interface. This could support future variants, but adds indirection without an evidenced need for this task.

The response selected the small clarification/test option. The production cutoff and executable diffusion/selection logic were retained.

## Before/after evidence

The [historical diff](https://github.com/HashAndCheddar/CS4928-Project/compare/a3704ea1b5cf30a513b0e945af55613de8c248a7...c936f52cc02d0e0b5f2d70d87df29ea71233195a) contains:

| Artefact | Change and what it establishes |
| --- | --- |
| `research/event_a/run.py` | One comment at the Spotify load says to change the network and date window together. No executable production change. |
| `test/test_event_a.py` | New 34-line test: start included, split-time review belongs only to late, overall end excluded, adjacent windows disjoint and complete for the fixture. |
| `research/event_a/REPORT.md` | Maintenance rationale, alternatives, response and limits recorded. |

Run the local contract check from the repository root:

```bash
python -m unittest test.test_event_a -v
```

The later final-draft verification reran this test together with the ten RQ2 tests: all 11 passed. This later run does not establish the date of the historical execution.

The saved [split_sensitivity.csv](../event_a/results/split_sensitivity.csv) records a selection/count analysis. Moving the split from 17 to 18 February changes early/late review counts from 9,703/12,801 to 10,676/11,828, reassigning 973 reviews while preserving 22,504 overall. Continuing/left/joined cohort counts change from 1,397/131/202 to 1,402/145/183. The alternative-cutoff analysis did not recompute diffusion coverage or overwrite the original Event A outputs.

## Conclusion and accepted trade-off

The evidence supports retaining the simple structure for these local maintenance tasks. The clarification makes the dataset/date dependency visible and the test records the window boundary contract. It does not show that every newcomer can work independently, or establish that another cutoff is scientifically better. A contributor still needs the research rationale for choosing a dataset/window. Comments can become stale, tests need maintenance, and the timing model's realism remains a limitation.

Earlier repository labels and the supplied workbook's Event B cells described the RAG extension. That labelling conflicts with the official task. This dated clarification preserves the earlier commit history while separating the maintenance response from RQ2. The workbook should retain original predictions and identify later corrections as later corrections.
