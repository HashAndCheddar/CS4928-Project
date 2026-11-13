# RQ2 / Event B: retrieval-augmented memory (G27 / P28)

**RQ2:** How does Retrieval Augmented memory affect information diffusion coverage compared to the paper's perfect memory baseline when participants can retrieve only a fixed amount of previously encountered information items in a code review network?

Event B is this extension. It changes the paper's model, which assumes every participant remembers and passes on everything they have ever seen.

## Prediction (recorded in the tracker before the change)

The RAG system should perform at least equal to, or slightly worse than, perfect memory because of limited retrieval.

## Setup

- **Network:** the full Trivago network used for RQ1 (364 participants, 2,442 reviews). We use the same review-end-time model and the same strict rule that information only moves into reviews that end later.
- **Information items:** each participant starts with one synthetic note, such as *"Caching: cache invalidation must be changed together with its config file after an incident last quarter."* Notes are distinct and generated from a fixed seed (`items.py`).
- **Review queries:** each review gets a seeded query about a component in one of its members' topic areas.
- **Conditions** (same network, timings and items):
  - `perfect`: every member shares everything they know. This is the paper's baseline.
  - `rag_5`: each member retrieves the **top-5** notes in their own memory by cosine similarity to the review query, and shares those.
  - `random_5`: control. Each member shares 5 random notes from memory. This separates the effect of the limit from the effect of semantic choice.
  - `rag_5_generation` (optional, `--generate`): the notes retrieved for `rag_5` are given to an LLM through OpenRouter, which writes the review comment. Only notes it cites, and that were actually offered, are passed on. Invalid citations are dropped and counted. Responses are cached, so a rerun repeats the same result at no cost.
- **Coverage:** the fraction of the network each note reaches, excluding its owner. With perfect memory this is exactly the paper's normalized range.

## Validation

Perfect memory reproduces the RQ1 result exactly. Its range distribution equals `research/rq1/results/normalized_ranges.csv` row for row; the run checks this and stops if it does not. Its Table 5 rows are 0.67 / 0.72 / 0.81 / 0.83 / max 0.85, the paper's values. Unit tests (`test/test_rq2.py`) check the following:

- On 25 random networks with many same-time reviews, perfect memory reaches the same set as the authors' `single_source_dijkstra_hyperedges`.
- Bounded memory never reaches more than perfect memory.
- When k is at least the network size, RAG equals perfect memory.
- Generation passes only notes it validly cited, and replays from the cache.

## Results (Trivago, k = 5, seed 0)

The embeddings were OpenRouter `openai/text-embedding-3-small` (256 dimensions), and the generation model was `openai/gpt-4.1-nano` (temperature 0).

Each `top_q` column shows the largest coverage value that at least that fraction of notes exceeds. This is the same rule as the paper's Table 5.

| Condition | Max | Median | Mean | top 0.7 | top 0.5 | top 0.3 | top 0.1 | Notes reaching ≥ 0.5 | Notes reaching nobody |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Perfect memory | 0.85 | 0.73 | 0.62 | 0.67 | 0.72 | 0.81 | 0.83 | 285 / 364 | 7 |
| Random-5 (control) | 0.49 | 0.10 | 0.12 | 0.04 | 0.09 | 0.16 | 0.24 | 0 / 364 | 7 |
| RAG top-5 (retrieval only) | 0.62 | 0.04 | 0.07 | 0.01 | 0.03 | 0.06 | 0.17 | 3 / 364 | 7 |
| RAG top-5 + generation | 0.35 | 0.02 | 0.04 | 0.00 | 0.01 | 0.03 | 0.10 | 0 / 364 | 60 |

7 notes reach nobody in every condition, because their owners only appear in reviews where they are the sole participant.

- **The prediction is challenged.** Bounded RAG memory is far worse than perfect memory, not "equal or slightly worse". Median coverage falls from 0.73 to 0.04 with retrieval, and to 0.02 once an LLM writes the review. The best-spread note falls from 0.85 to 0.62 and then 0.35.
- **Semantic retrieval spreads less than random retrieval** (median 0.04 vs 0.10). Notes that match many queries keep being retrieved and travel further (max 0.62 vs 0.49), but most notes are rarely chosen. Retrieval concentrates diffusion instead of widening it.
- **Generation narrows it further.** In the 1,576 reviews where sharing could change someone's memory, the model was offered 12,600 notes and cited 5,297 (42%). It produced no unparseable replies and no invalid citations. The other 866 reviews could not change memory and were skipped without a call. 60 notes were never passed on by anyone.
- **The embedding choice changes details, not the conclusion.** An earlier run of the same setup with the local TF-IDF fallback gave RAG top-5 a max of 0.66, median 0.04 and mean 0.07. Those numbers are from that run's console output; it is not stored in `results/`.

**Cost:** the final run made 328 OpenRouter calls at a reported $0.022. The rest of the 1,576 generation reviews were replayed from the cache, written by an earlier run that crashed on a dropped connection after 1,844 reviews. That run's cost was not recorded. At the same per-call rate, the whole experiment cost about $0.10. Rerunning from the cache makes no calls.

Files are in [`results/trivago/`](./results/trivago/): `coverage.csv` (per note), `normalized_ranges.csv` / `ranges.csv` (cumulative, same format as RQ1), `summary.csv`, and `run.json` (configuration, generation statistics, calls and reported cost).

## Design decision

**Options considered:**

1. Add memory limits inside the authors' `simulation/minimal_distances.py`. Dijkstra computes reachability for one source at a time, so it cannot express a participant choosing *which* of many items to pass on. Changing it would also put the RQ1 reproduction at risk.
2. Add a separate item-level engine in `research/rq2/` that leaves the authors' code untouched. The memory policy is one `share(review, members, memory)` function. **We chose this option.**
3. Use the multi-package architecture sketched earlier in the README (memory base classes, retrieval index package, network adapters). It is more flexible, but it adds indirection the experiment does not need.

**Trade-off:** option 2 hides the one decision that varies, *what a reviewer passes on*, behind a small interface, so perfect, random, RAG and RAG + generation differ only in that function. Its cost is a second diffusion implementation alongside the authors' code. We control that cost by requiring the perfect-memory policy to match both the authors' algorithm (tests) and the RQ1 output (every run).

## Limitations

- The notes and queries are synthetic, with one note per participant. Real review knowledge is not this uniform, so the size of the gap depends on how notes and queries are generated, not only on k.
- The results come from one seed, one k and one generation model. The template text is repetitive, so equal similarity scores are broken by note index.
- k limits what each member retrieves per review, not what they remember. The baseline's timing limitation (review end times) carries over unchanged from RQ1 and Event A.
- LLM output can vary between providers even at temperature 0. The cache, not the model, is what makes the generation condition repeatable.

## Run

```bash
python -m research.rq2.run                  # TF-IDF fallback if no key; perfect, random-5, RAG-5
export OPENROUTER_API_KEY=...               # or put OPENROUTER_API_KEY=... in a repo-root .env (gitignored)
python -m research.rq2.run --generate       # OpenRouter embeddings + RAG with generation
```

Options: `--k`, `--seed`, `--embedder {auto,openrouter,tfidf}`, `--embedding-model` (default `openai/text-embedding-3-small`, 256 dimensions), `--chat-model` (default `openai/gpt-4.1-nano`) and `--max-cost` (USD cap on OpenRouter-reported cost, default 1.00). Caches are written to `research/rq2/cache/`. Commit them to make the OpenRouter results reproducible without a key.
