# Evidence index

The experiment data inspected for this synthesis are pinned to [40f8c85](https://github.com/HashAndCheddar/CS4928-Project/tree/40f8c8556f11cbc9d8e38a7cd3aac6b12a0adb20). Relative links below refer to the published snapshot.

| Claim | Evidence |
| --- | --- |
| RQ1 method and distribution | [Runner](research/rq1/run.py), [normalized ranges](research/rq1/results/normalized_ranges.csv), [absolute ranges](research/rq1/results/ranges.csv) |
| RQ1 later reference audit | [Verification record](typst/verification.md); 82,208 parsed Trivago rows matched, without claiming compressed-byte identity |
| Event A windows and cohort results | [Runner](research/event_a/run.py), [report](research/event_a/REPORT.md), [turnover CSV](research/event_a/results/turnover.csv) |
| Timing decision | [Loader](simulation/model.py), [path algorithm](simulation/minimal_distances.py), [paper](https://doi.org/10.1007/s10664-024-10442-y) |
| Event B maintenance response | [Report](research/event_b/REPORT.md), [boundary test](test/test_event_a.py), [before/after diff](https://github.com/HashAndCheddar/CS4928-Project/compare/a3704ea1b5cf30a513b0e945af55613de8c248a7...c936f52cc02d0e0b5f2d70d87df29ea71233195a) |
| Cutoff sensitivity counts | [CSV](research/event_a/results/split_sensitivity.csv); alternative-cutoff coverage was not recomputed |
| RQ2 design and configuration | [Sharing-policy engine](research/rq2/diffusion.py), [runner](research/rq2/run.py), [original run metadata](research/rq2/results/trivago/run.json) |
| RQ2 numeric results | [Per-note coverage](research/rq2/results/trivago/coverage.csv), [summary](research/rq2/results/trivago/summary.csv) |
| Cache-only reproducibility | [Replay helper](research/rq2/replay.py), [saved verification](typst/repro-verification.json), [pinned environment](requirements-verified.txt) |
| Tests | [RQ2 policy tests](test/test_rq2.py), [Event A boundary test](test/test_event_a.py), [final test output](typst/validation-tests.txt) |
| Graph inputs and provenance | [CSV copies and SHA-256/source manifest](typst/figures/sources.json), [graph builder](typst/figures/regenerate.py) |
| Final paper | [PDF](typst/report.pdf), [Typst main](typst/main.typ), [build guide](typst/README.md) |

The readability account is the team's retrospective report, not a timed newcomer study. The pre-Event-B state (Event A entries and Week 9 decision) is fixed by the coordinator's frozen tracker export of 12 November 2026; the timing of earlier predictions relative to their results rests on the tracker. The `FINAL` tag identifies this synthesis and its reproduction tools; it does not backdate those records.
