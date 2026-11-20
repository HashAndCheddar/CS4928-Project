# Verification record

Validation date: 19 November 2026. These checks were carried out during report preparation. They do not establish when the group originally made predictions or ran experiments.

## Sources and environment

- Group repository: https://github.com/HashAndCheddar/CS4928-Project
- Inspected commit: `40f8c8556f11cbc9d8e38a7cd3aac6b12a0adb20`
- Public reference: https://zenodo.org/records/8042256/files/trivago.csv.bz2
- Reference compressed-file MD5: `a5e1a6d5230ac8c1888a711bd91f0420`, matching the record's published value.
- Supplied documents: `Project Brief and Rubric(1).docx`, `Student Tracker.xlsx`, and `conference-latex-template.zip`.
- Validation runtime: Windows, Python 3.12.14, NumPy 2.5.5, pandas 3.0.1, tqdm 4.70.1. The project's recommended Python version is 3.11. This is a later environment check, not a reconstruction of the original environment.
- PDF compiled using the Python Typst binding 0.15.2; the standalone source requires no Universe packages.

## Repository tests

Command from a local repository copy:

```text
python -m unittest discover -v
```

Final result:

```text
Ran 27 tests in 34.244s
OK (skipped=1)
```

26 tests passed. `test.test_results.ResultsTest.test_results` was skipped because no Zenodo access token was provided. A separate public download and parsed-data comparison was therefore used for Trivago. This does not substitute for an all-dataset checksum audit.

The passing tests cover the model/network interfaces, two minimal-distance implementations, simulation runners, Event A boundaries and the ten RQ2 tests. Those RQ2 tests include 25 generated-network comparisons with the authors' reachability algorithm, simultaneous-review handling, bounded selection, large-k equivalence, deterministic ties, repeatable content, embedding normalization, citation filtering and response-cache replay.

An initial run failed to import two test modules because tqdm was missing from the validation runtime. After installing that declared project dependency, the complete run above passed. No project source change was required.

## RQ1 public-reference audit

The simulation tests regenerated the three Trivago distance columns. Both regenerated and Zenodo CSVs were parsed with source and target as strings, sorted by those two identifiers and compared column by column.

| Check | Result |
|---|---|
| Reference rows | 82,208 |
| Source identifiers equal | Yes |
| Target identifiers equal | Yes |
| Shortest distances equal | Yes |
| Fastest distances equal | Yes |
| Foremost distances equal | Yes |
| Entire parsed table equal | Yes |
| Maximum other-participant reach | 310 |
| Maximum normalized coverage | 0.8516483516483516 |
| Median other-participant reach | 267 |
| Recomputed normalized range CSV matches committed parsed values after `%g` serialization | Yes |
| Recomputed absolute range CSV matches committed parsed values after `%g` serialization | Yes |

The regenerated compressed CSV MD5 was `c2d3ca5c12cdd34222b924997c1c16c1`, so **compressed-byte identity was not established**. The parsed values were identical. The unrounded recomputed CDF differs from the limited-precision saved CDF by at most approximately 4.84×10⁻⁷ (normalized) and 4.95×10⁻⁷ (absolute). These are cumulative probabilities, not errors in underlying participant coverage. Applying the same `%g` serialization recovers the saved values exactly. A strict 10⁻⁷ preregistered tolerance therefore needs to identify both the intended quantity and its precision.

## RQ2 offline cache replay

The run was invoked with explicit OpenRouter embeddings and generation, while the API-key function was forced to return `None`. This prevents a network fallback or new paid response. Existing result files were saved for comparison and restored after validation.

Equivalent CLI options, provided that neither the environment nor a repository `.env` supplies a key:

```text
python -m research.rq2.run --embedder openrouter --generate
```

The default no-key command selects TF-IDF, so it is not an exact replay of the committed OpenRouter experiment.

| Check | Result |
|---|---|
| Parsed `coverage.csv` identical | Yes |
| Parsed `normalized_ranges.csv` identical | Yes |
| Parsed `ranges.csv` identical | Yes |
| Parsed `summary.csv` identical | Yes |
| Generation evaluations | 1,576 |
| Generation cache hits | 1,576 |
| Offered item instances | 12,600 |
| Valid cited item instances | 5,297 |
| Unparseable responses | 0 |
| Invalid citation numbers | 0 |
| OpenRouter calls | 0 |
| Replay reported API cost | 0 |
| Each bounded condition's per-item coverage at most perfect memory | Yes |

The regenerated CSV files differed as bytes in this Windows checkout; their parsed contents were identical. File-byte equality is not claimed. The committed run metadata describes the original/resumed run (328 calls, 1,248 cache hits and reported cost USD 0.021568); it should not be replaced by the metadata from the later all-cache replay. The original report also states that an earlier interrupted run's cost was not recorded.

Recorded summary, based on rounded per-item coverage:

| Condition | Max | Median | Mean |
|---|---:|---:|---:|
| perfect | 0.85 | 0.73 | 0.6212 |
| random_5 | 0.49 | 0.10 | 0.1213 |
| rag_5 | 0.62 | 0.04 | 0.07299 |
| rag_5_generation | 0.35 | 0.02 | 0.03918 |

## Event A consistency check

The perfect-sharing item engine was applied to the Spotify network and the original early/late windows. This is an additional implementation consistency check, not a fresh rerun of Event A's original all-source Dijkstra driver. Original-window summaries matched the stored report and CSVs.

| Window | Participants | Reviews | Max | Median |
|---|---:|---:|---:|---:|
| Full | 1,730 | 22,504 | 0.85 | 0.73 |
| Early | 1,528 | 9,703 | 0.65 | 0.10 |
| Late | 1,599 | 12,801 | 0.76 | 0.46 |

| Cohort | Participants | Experienced | Early median | Late median |
|---|---:|---:|---:|---:|
| Continuing | 1,397 | 379 | 0.12 | 0.50 |
| Early only | 131 | 3 | 0.01 | — |
| Late only | 202 | 0 | — | 0.02 |

Alternative split-date coverage was not rerun. No claim is made that coverage is insensitive to the split, that activity-only cohorts represent actual staff turnover, or that the observed differences are causal.

## Final validation

On 20 November 2026, the pinned requirements were installed in a clean CPython 3.12.14 environment. The cache-only RQ2 replay matched all four committed CSVs as parsed values, made zero API calls, and preserved the SHA-256 hashes of the committed results and caches. Its full output is in `repro-verification.json`.

The same clean environment passed the 11 Event A/RQ2 tests. The earlier 26-pass/1-skip audit above is a separate check; final test output is retained in `validation-tests.txt`. The report build uses Python Typst 0.15.2 and the compiler's default fonts. Graphs are regenerated from the saved CSVs without new experiments.

Historical evidence links in the paper refer to state `40f8c8556f11cbc9d8e38a7cd3aac6b12a0adb20`. The `FINAL` tag identifies the published synthesis and reproduction instructions; it does not establish when earlier predictions were recorded. The maintenance readability account is retrospective, as stated in the paper.
