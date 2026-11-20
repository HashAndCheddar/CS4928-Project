# Information Diffusion through Code Review

CS4928 · Group G27 · Project P28 · University of Limerick

[**Read the paper (PDF)**](typst/report.pdf) · [Typst source](typst/main.typ) · [Evidence index](EVIDENCE.md) · [Reproduction guide](REPRODUCING.md) · [FINAL snapshot](https://github.com/HashAndCheddar/CS4928-Project/tree/FINAL)

We reproduce the Trivago information-diffusion range from [Dorner et al.](https://doi.org/10.1007/s10664-024-10442-y), compare Spotify activity windows, examine a local maintenance task, and test bounded retrieval and generation.

## Results

| Work | Main result | Evidence |
| --- | --- | --- |
| RQ1: Trivago reproduction | Maximum reach 310/364 (0.85); median 267/364 (0.73). Reported range reproduced at the paper's precision. | [Runner](research/rq1/run.py), [range output](research/rq1/results/normalized_ranges.csv), [audit](typst/verification.md) |
| Event A: Spotify windows | Median coverage rises from 0.10 to 0.46. Late-only participants have median 0.02 versus 0.50 for continuing participants. | [Report](research/event_a/REPORT.md), [cohort results](research/event_a/results/turnover.csv) |
| Event B: newcomer maintenance | Retain the structure; clarify the dataset/date dependency and test window boundaries. Readability is a retrospective team account. | [Report](research/event_b/REPORT.md), [boundary test](test/test_event_a.py), [historical diff](https://github.com/HashAndCheddar/CS4928-Project/compare/a3704ea1b5cf30a513b0e945af55613de8c248a7...c936f52cc02d0e0b5f2d70d87df29ea71233195a) |
| RQ2: bounded sharing | Median coverage: perfect memory 0.73; random-5 0.10; semantic top-5 0.04; top-5 with generation 0.02. | [Report](research/rq2/REPORT.md), [summary](research/rq2/results/trivago/summary.csv), [per-note results](research/rq2/results/trivago/coverage.csv) |

Earlier commits labelled the RAG extension as Event B. The official Event B concerns newcomer maintenance; RAG is our separate RQ2 extension. The dated clarification and historical evidence are retained in the reports.

## Reproduce the saved RQ2 results

Tested on Windows with CPython 3.12.14. The verified dependencies, including their transitive dependencies, are pinned in `requirements-verified.txt`.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-verified.txt
.\.venv\Scripts\python.exe -m research.rq2.replay
```

macOS/Linux with Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-verified.txt
.venv/bin/python -m research.rq2.replay
```

The replay uses the committed OpenRouter caches, ignores API keys, and fails on a cache miss. It writes to a new `_reproduction/` directory, compares all four CSVs, and verifies that the committed results and caches are unchanged. Expected output:

```text
PASS: all saved CSV values matched; no API calls; committed inputs unchanged.
```

[Saved replay verification](typst/repro-verification.json) records the check. The original experiment's metadata remains in [run.json](research/rq2/results/trivago/run.json). A default no-key run selects TF-IDF and is a different experiment; use the replay command above for the recorded OpenRouter results.

## Tests and full recomputation

Using the virtual environment's interpreter:

```bash
python -m unittest discover -v
python -m research.rq1.run
python -m research.event_a.run
```

RQ1 and Event A recompute distances and overwrite their generated outputs. Use a disposable checkout for those commands. The token-dependent Zenodo test is skipped without its optional dependencies/token; the separate public Trivago audit and test output are documented in [verification](typst/verification.md). Detailed commands, model settings, precision checks and limitations are in [REPRODUCING.md](REPRODUCING.md).

## Build the paper and graphs

```bash
python -m pip install -r typst/requirements-build.txt
python typst/build.py
```

Alternatively: `typst compile typst/main.typ typst/report.pdf`.

The two figures are included as SVG and PNG files. Their CSV inputs and source hashes are in [typst/figures](typst/figures); the [Typst guide](typst/README.md) explains regeneration. Compiling the paper requires no plotting package or API key.

## Scope and provenance

Coverage measures potential outward reach, not learning or review quality. Event A cohorts describe activity rather than employment. RQ2 uses synthetic notes, one seed, k=5 and one embedding/generation configuration. The historical freeze/prediction records are incomplete; `FINAL` identifies this published snapshot, not an earlier prediction date.

Based on the authors' [simulation](https://github.com/michaeldorner/information-diffusion-boundaries-in-code-review) and [research artefacts](https://zenodo.org/records/8042256). Their licence and attribution are retained.
