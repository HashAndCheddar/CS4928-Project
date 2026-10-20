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

RQ1 asks: **To what result can the information diffusion range reported by the paper be repeated using the authors' algorithm and Trivago's code review dataset?** We run the original simulation on the full Trivago network, with no participant sample restriction:

```bash
python -m research.rq1.run
```

The script regenerates the authors' shortest, fastest and foremost distances, then applies the range calculation from `notebooks/ranges.ipynb`. For each participant, range is the number of other participants they can reach via time-ordered reviews; normalized range divides that count by the total participant count. Trivago has 364 participants and 2,442 review channels. The two cumulative distributions are written to:

- `research/rq1/results/normalized_ranges.csv`
- `research/rq1/results/ranges.csv`

The reproduced values match the Trivago values in Tables 5 and 6 of the paper:

| Paper table | Paper percentile | Paper Trivago range | Reproduced range |
| --- | ---: | ---: | ---: |
| 5 (normalized) | 0.70 | 0.67–0.85 | 0.67–0.85 |
| 5 (normalized) | 0.50 | 0.72–0.85 | 0.72–0.85 |
| 5 (normalized) | 0.30 | 0.81–0.85 | 0.81–0.85 |
| 5 (normalized) | 0.10 | 0.83–0.85 | 0.83–0.85 |
| 5 (normalized) | max | 0.85 | 0.85 |
| 6 (absolute) | 0.70 | 245–310 | 245–310 |
| 6 (absolute) | 0.50 | 266–310 | 266–310 |
| 6 (absolute) | 0.30 | 296–310 | 296–310 |
| 6 (absolute) | 0.10 | 309–310 | 309–310 |
| 6 (absolute) | max | 310 | 310 |

This reproduces the reported RQ1 range result for Trivago. The paper's maximum reachable range is 310 other participants (about 85% of the 364-person network). The regenerated Trivago distance CSV also has the same MD5 checksum as the authors' Zenodo result. Range-over-time files are not part of this RQ1 answer.

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
