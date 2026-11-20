# Typst paper

Open this folder in Texpile and select `main.typ` as the main document.

- `main.typ`: title, authors, abstract, references and section includes.
- `sections/`: RQ1; events/design; RQ2/discussion.
- `ieee-local.typ`: IEEE layout using the compiler's default fonts.
- `evidence.typ` and `refs.bib`: evidence links and references.
- `figures/`: vector/PNG figures, input CSVs, hashes and regeneration script.
- `report.pdf`: compiled paper.

## Build

From the repository root:

```bash
python -m pip install -r typst/requirements-build.txt
python typst/build.py
```

The recorded Python Typst binding is 0.15.2. A standalone CLI can also build the source:

```bash
typst compile typst/main.typ typst/report.pdf
```

## Regenerate figures

```bash
python -m pip install -r typst/figures/requirements.txt
python typst/figures/regenerate.py
python typst/build.py
```

The script reads the adjacent CSV copies and records their hashes and immutable repository source links in `figures/sources.json`. It performs no new experiment or API call. The Event A figure reports window/cohort medians; the RQ2 figure shows all 364 saved per-note coverage values.

See [verification.md](verification.md), [repro-verification.json](repro-verification.json), and [validation-tests.txt](validation-tests.txt) for the validation evidence. Original experiment data and caches remain under `research/`.
