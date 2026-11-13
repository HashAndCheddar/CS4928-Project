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

## Event A

Event A applies the same coverage measure to the Spotify network and compares participants who stay, leave or join between two 14-day halves of February 2020. See `research/event_a/REPORT.md`.

```bash
python -m research.event_a.run
```

The range distributions and turnover table are written to `research/event_a/results/`.

## Research Question 2 (Event B)

RQ2 is our Event B. It compares the paper's perfect-memory baseline with retrieval-augmented memory on the same Trivago network. Each participant starts with one synthetic information item. In each review, a member can retrieve only their **top-5** most relevant known items (by embedding similarity to the review query) and pass those on. A random-5 control and an optional LLM generation step (through OpenRouter, passing on only the items the model cites) are included. The perfect-memory run reproduces the RQ1 range distribution exactly. See `research/rq2/REPORT.md`.

```bash
python -m research.rq2.run              # no key: local TF-IDF embeddings
export OPENROUTER_API_KEY=...           # or OPENROUTER_API_KEY=... in a repo-root .env (gitignored)
python -m research.rq2.run --generate   # OpenRouter embeddings + RAG with LLM generation (cost-capped)
```

```text
research/rq2/
├── run.py          # conditions, RQ1 check, outputs
├── diffusion.py    # time-ordered item diffusion; perfect / random-k / RAG / RAG + generation policies
├── items.py        # seeded synthetic items and review queries
├── embeddings.py   # OpenRouter embeddings (cached) or TF-IDF fallback
├── generation.py   # grounded LLM comment, citation validation, response cache
├── openrouter.py   # API key from env/.env, retries, cost cap
├── cache/          # embedding and LLM response caches
└── results/<network>/
```

## Credits

Based on the [original simulation](https://github.com/michaeldorner/information-diffusion-boundaries-in-code-review) by Michael Dorner, the [paper](https://link.springer.com/article/10.1007/s10664-024-10442-y) and the [research artefacts](https://zenodo.org/records/8042256). The authors' MIT licence and attribution are retained.
