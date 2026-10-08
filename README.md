# Information Diffusion through Code Review

## CS4928: Theory and Practice of Software Design | University of Limerick

We're reproducing the information diffusion results from Dorner et al. using Trivago's code review dataset, then extending the simulation with a RAG-based memory system.

## Research Questions

1. To what result can the information diffusion range reported by the paper be repeated using the authors algorithm and Trivago's code review dataset?

2. How does Retrieval Augmented memory affect information diffusion coverage compared to the paper's perfect memory baseline when participants can retrieve only a fixed amount of previously encountered information items in a code review network?

## Setup (Python 3.11)

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover
```

## Research Question 1

RQ1 is a local replication: run the authors' existing simulation, reproduce the Trivago analysis and compare it with the paper's results. No custom simulation wrappers or RAG components are needed.

Run the authors' original Trivago simulation:

```bash
python -m simulation.run --select trivago
```

This calculates shortest, fastest and foremost temporal distances, saved in `data/minimal_distances/`.

To view the authors' existing Trivago figure and range results on macOS:

```bash
open reports/png/range_over_time_trivago.png
open reports/csv/ranges.csv
```

To reproduce plots using the authors' own notebook:

```bash
python -m pip install jupyterlab matplotlib ipywidgets
cd notebooks
jupyter lab ranges.ipynb
```

1. Keep only the Trivago analysis, loading `../data/minimal_distances/trivago.pickle.bz2`.
2. Compare the calculated percentile ranges and maximum with the Trivago values in Tables 5 and 6 of the paper.
3. Create `research/RQ1/` for our tables and figures, export there instead of `reports/`, and explain any differences in the report.

## Research Question 2

We plan to build a full RAG system with embeddings, vector retrieval and grounded LLM generation. Participants will only retrieve previously encountered information, up to a fixed limit, so we can compare diffusion coverage against the original perfect memory baseline.

### Suggested architecture

```text
research/rq2/
├── run.py              # run RQ2 experiments
├── network.py          # adapt review channels and timings
├── items.py            # information items and review queries
├── engine.py           # temporal diffusion loop
├── metrics.py          # coverage and baseline comparisons
├── memory/
│   ├── base.py         # common memory interface
│   ├── perfect.py      # perfect-memory baseline
│   ├── random_k.py     # bounded random retrieval control
│   └── rag.py          # bounded semantic retrieval
├── retrieval/
│   ├── embedder.py     # cached text embeddings
│   └── index.py        # retrieve from encountered items only
├── generation.py       # grounded LLM output and validation
├── requirements.txt    # RQ2 dependencies
├── notebooks/
└── tests/
results/rq2/            # RQ2 tables, figures and caches
```

## Credits

Based on the [original simulation](https://github.com/michaeldorner/information-diffusion-boundaries-in-code-review) by Michael Dorner, the [paper](https://link.springer.com/article/10.1007/s10664-024-10442-y) and the [research artefacts](https://zenodo.org/records/8042256). The authors' MIT licence and attribution are retained.
