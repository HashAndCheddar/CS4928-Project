# Information Diffusion through Code Review

CS4928, Group G27, Project P28, University of Limerick.

We reproduce the bounded Trivago range result from [Dorner et al.](https://doi.org/10.1007/s10664-024-10442-y), transfer the method to Spotify activity windows, examine a local newcomer-maintenance task, and compare perfect sharing with bounded retrieval and generation. This repository builds on the authors' [simulation](https://github.com/michaeldorner/information-diffusion-boundaries-in-code-review) and [research artefacts](https://zenodo.org/records/8042256). Their licence and attribution are retained.

## Research questions and results

- **RQ1:** To what extent can the paper's Trivago diffusion range be reproduced using the authors' algorithm and dataset? We use the full 364-participant, 2,442-review network. Maximum reach is 310 other participants (0.85); ordinary median reach is 267 (0.73). The paper's upper-70% range is 245-310 (0.67-0.85). Rounded table agreement, parsed source-level agreement, and compressed-file identity are separate checks.
- **RQ2:** How does bounded retrieval affect diffusion relative to perfect memory? On Trivago, seed 0 and k=5, recorded median coverage is 0.73 for perfect memory, 0.10 for random-5, 0.04 for semantic top-5, and 0.02 for top-5 with generation. Notes and queries are synthetic; these results do not measure review quality or human learning.

**Event A** is the Spotify early/late activity-window analysis. **Event B** concerns maintenance by a contributor without prior review involvement. RQ2 is a separate extension. Earlier commits called the RAG extension Event B; this clarification preserves that history and uses the official P28 event task. The maintenance contributor's report of readability is a retrospective team account; no contemporaneous timings or walkthrough notes were retained.

## Start with the saved experiment, without API calls

The later Windows validation used **CPython 3.12.14**, NumPy 2.5.5, pandas 3.0.1 and tqdm 4.70.1. These versions are captured in `requirements-verified.txt`. The original README recommended Python 3.11 with unpinned dependencies; the later environment is not claimed to be the historical one.

Windows PowerShell, from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-verified.txt
.\.venv\Scripts\python.exe -m research.rq2.replay
```

macOS/Linux, with Python 3.12 available:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-verified.txt
.venv/bin/python -m research.rq2.replay
```

Use the virtual environment's interpreter for the commands below. The examples use `python` for that interpreter; activation is optional when its full path is used.

The replay:

1. Copies the two committed OpenRouter caches into a new `_reproduction/rq2-<timestamp>/` directory.
2. Runs the existing Trivago engine with k=5, seed 0, OpenRouter embeddings and generation. It ignores API keys and fails if a required cache entry is missing; it cannot request a new response.
3. Compares the parsed values of all four generated CSVs with the committed CSVs, including their rows, columns and types.
4. Checks that every generation response was cached, there were zero API calls, and the committed cache/result files retained their SHA-256 hashes.
5. Saves separate replay metadata and `verification.json` under `_reproduction/`.

Expected outcome: `PASS: all saved CSV values matched; no API calls; committed inputs unchanged.` The replay's call/cache statistics differ from the original mixed fresh/cached run. It does not overwrite that original `run.json` or claim CSV byte identity across platforms.

## Commands, evidence and interpretation

| Work | Command | Saved evidence |
| --- | --- | --- |
| Bounded RQ1 reproduction | `python -m research.rq1.run` | `research/rq1/results/{ranges,normalized_ranges}.csv`; regenerated Trivago distances in `data/minimal_distances/` |
| Event A | `python -m research.event_a.run` | `research/event_a/results/{ranges,normalized_ranges,turnover}.csv` and `research/event_a/REPORT.md` |
| Event B boundary contract | `python -m unittest test.test_event_a -v` | `research/event_b/REPORT.md`, `test/test_event_a.py`; [historical maintenance diff](https://github.com/HashAndCheddar/CS4928-Project/compare/a3704ea1b5cf30a513b0e945af55613de8c248a7...c936f52cc02d0e0b5f2d70d87df29ea71233195a) |
| RQ2 saved OpenRouter experiment | `python -m research.rq2.replay` | `research/rq2/results/trivago/`; isolated replay verification under `_reproduction/` |
| RQ2 policy checks | `python -m unittest test.test_rq2 -v` | `test/test_rq2.py` |
| Complete test suite | `python -m unittest discover -v` | Save the console output with interpreter/package versions and the inspected commit |

The RQ1 and Event A commands recompute distances and **overwrite their corresponding generated outputs**. Event A uses all-source searches and can take considerably longer than the cached RQ2 replay. Use a disposable checkout or preserve existing outputs before either recomputation. No exact runtime is promised.

Coverage excludes the source/owner from the numerator and divides by the full active network/window population. Event A uses the same end-time rule and review selection `[start, end)`. The early window is 3 February up to 17 February 2020; the late window is 17 February up to 2 March. Their denominators differ (1,528 and 1,599 active participants). Activity cohorts are not employment records. Outward reach does not measure what newcomers receive.

The saved `split_sensitivity.csv` records counts for alternative cutoffs. It is a data-selection analysis: coverage was not recomputed for those alternative splits. Event B's local change added one dataset/date comment and a boundary test without changing production selection logic. This supports the small maintenance response; it does not establish general newcomer performance or validate the timing model.

## Tests and reference comparison

The later draft audit recorded 27 tests run: 26 passed and one token-dependent Zenodo test was skipped. Report skips explicitly. `test.test_results` requires both `requests` and `ZENODO_ACCESS_TOKEN`; without them it is skipped, so a green suite alone is not evidence of an all-dataset reference audit.

A separate public Trivago comparison during that audit matched all 82,208 parsed source-target distance rows. The regenerated compressed bytes did not have the reference MD5 in that environment. Therefore the earlier README's unqualified same-MD5 claim should not be used as the later audit's result. See `typst/verification.md` for the environment, distinction between coverage/CDF precision, and scope of the check.

The RQ2 runner compares its perfect-memory distribution numerically with the saved RQ1 CSV using `np.allclose` (`atol=1e-6`, default relative tolerance). Its console word "exactly" does not mean byte identity or the tracker's separate 1e-7 source-level criterion. The policy tests also compare reachable sets with the original algorithm on generated networks. The replay helper makes the stronger, explicit check that regenerated saved CSV values match the committed parsed values.

## Local TF-IDF and fresh provider runs

```bash
python -m research.rq2.run --embedder tfidf
```

This is a different embedding condition from the committed OpenRouter experiment and writes into the same default result directory. Run it only in a disposable checkout if preserving the recorded experiment. A default no-key `research.rq2.run` also selects TF-IDF, so it is not an exact replay of the published OpenRouter results.

Fresh OpenRouter responses are optional and unnecessary for replay. If deliberately running a new experiment in a separate checkout, supply your own `OPENROUTER_API_KEY` through the environment or a gitignored `.env`, then run:

```bash
python -m research.rq2.run --embedder openrouter --generate --max-cost 1.00
```

This may call a paid provider on cache misses and writes default results/caches. The cap applies to provider-reported cost during that invocation; it is not a guarantee of total billing. Never commit API keys. Temperature 0 does not guarantee identical fresh responses; the committed cache supplies the repeatable sampled generation results.

## Report and graphs

`typst/main.typ` includes the three files under `typst/sections/`. Keep the local IEEE template, bibliography, evidence helper and figures together. The source and PDF are included in this snapshot. Compile with Typst:

```bash
typst compile typst/main.typ typst/report.pdf
```

The report was checked with the Python Typst binding 0.15.2. To use that recorded build path instead of a separately installed CLI:

```bash
python -m pip install -r typst/requirements-build.txt
python typst/build.py
```

The figures are SVGs generated from committed CSVs; building the report needs no plotting package or API key. To regenerate the graphs independently:

```bash
python -m pip install -r typst/figures/requirements.txt
python typst/figures/regenerate.py
```

Each figure's copied CSV inputs, source URLs, source-state commit and SHA-256 hashes are recorded in `typst/figures/sources.json`. A graph regeneration is a later presentation step, not a new empirical experiment.

## Milestone provenance and finalisation

Evidence inspected at [40f8c85](https://github.com/HashAndCheddar/CS4928-Project/tree/40f8c8556f11cbc9d8e38a7cd3aac6b12a0adb20):

| Existing state | What can be inspected |
| --- | --- |
| [2e1b2ab](https://github.com/HashAndCheddar/CS4928-Project/commit/2e1b2ab12901a9a2bdb2d8f3376d4fc49c7886b0) | Initial RQs and proposed architecture |
| [da17616](https://github.com/HashAndCheddar/CS4928-Project/commit/da17616f4b7777ee0893f36d2352f2b89e2e523a) | Commit labelled M2_REPRO |
| [1a946b8](https://github.com/HashAndCheddar/CS4928-Project/commit/1a946b819a78d2d3079ea57d814b4cf6055e306c) | Event A analysis |
| [a3704ea](https://github.com/HashAndCheddar/CS4928-Project/commit/a3704ea1b5cf30a513b0e945af55613de8c248a7) | Parent code state for the maintenance response; confirm its relation to M4 |
| [c936f52](https://github.com/HashAndCheddar/CS4928-Project/commit/c936f52cc02d0e0b5f2d70d87df29ea71233195a) | Maintenance comment, boundary test and original Event B account |
| [04e6d6d](https://github.com/HashAndCheddar/CS4928-Project/commit/04e6d6d193336ad437ff5b734568078f56e81642) | RQ2 extension and later RAG-as-Event-B relabelling |

No published tags were returned during the 20 November 2026 review. The PRE_EVENT_A-labelled commit precedes the M2-labelled commit, so names alone do not prove the required freeze order. Confirm original workbook/version-history evidence and the actual M1/M4 states. If tags are added to existing commits now, state their actual creation date; do not describe them as contemporaneous predictions. The FINAL tag is being created for this reviewed synthesis on 20 November 2026. Use it consistently in the tracker and submission; it is not a historical preregistration tag.
