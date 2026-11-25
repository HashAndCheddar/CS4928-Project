#import "../evidence.typ": ev

= RQ2 Extension and Results

Each Trivago participant starts with one synthetic note about a software topic and component. Seeded review queries select a topic from a review member. We compare four policies: sharing all known notes, sharing up to five random notes, retrieving the five most relevant known notes, and passing retrieved notes through generation. The generation policy shares only notes with valid citations. The limit applies per member per review; previously received notes remain in memory.

The #ev("research/rq2/results/trivago/run.json", [recorded run]) uses seed 0, 256-dimensional `openai/text-embedding-3-small` embeddings and `openai/gpt-4.1-nano` generation through OpenRouter at temperature 0. Equal-ending reviews read the same prior memory state, preventing simultaneous reviews from forming an onward chain.

#figure(
  table(columns: 3,
    table.header[*Sharing policy*][*Max*][*Median*],
    [Perfect memory], [0.85], [0.73],
    [Random-5 control], [0.49], [0.10],
    [Semantic top-5], [0.62], [0.04],
    [Top-5 + generation], [0.35], [0.02],
  ),
  caption: [Trivago coverage, rounded to two decimals. Source: #ev("research/rq2/results/trivago/summary.csv", [summary CSV]).],
) <tab:rq2>

#figure(
  image("../figures/rq2-distributions.svg", width: 100%),
  caption: [Coverage distributions for 364 synthetic notes. Higher curves indicate a larger fraction of notes at or below the given coverage. Source: #ev("research/rq2/results/trivago/coverage.csv", [per-note results]).],
) <fig:rq2>

The results challenge our expectation of equal or slightly lower coverage. Median coverage falls from 0.73 to 0.04 with semantic retrieval and to 0.02 with generation: reductions of 69 and 71 percentage points using the rounded values. We did not add a numerical definition of "slightly" after seeing the results.

Semantic retrieval has a lower median than random selection but a higher maximum. Some notes spread widely while many spread little; this does not establish which policy produces better review advice. Generation narrows sharing further, citing 5,297 of 12,600 offered item instances (42%). A valid citation shows that a note was offered, not that the generated comment was correct.

We placed the sharing policies behind one `share(review, members, memory)` function in a separate #ev("research/rq2/diffusion.py", [item-level engine]): a Strategy, so each condition differs only in that function and the authors' code stays closed to modification. This avoids changing the original distance algorithm or adding a broader memory/retrieval framework. The cost is a second diffusion implementation. Equivalence tests and the runner's numerical RQ1 comparison check that its perfect-memory policy preserves the baseline.

= Verification and AI Use

The #ev("test/test_rq2.py", [tests]) compare perfect-memory reachability with the authors' algorithm on 25 generated networks. They also check equal-ending reviews, bounded sharing, large-limit equivalence, deterministic selection, citation filtering and cache replay.

A later audit recorded 26 passing tests and one skipped token-dependent Zenodo test. It matched 82,208 parsed Trivago reference rows and reproduced the saved RQ2 CSV values from cache without API calls. These checks validate the implementation, not historical prediction dates. Commands and versions accompany the report.

AI assisted writing and code inspection. Checking its initial account against the official handout and maintenance diff exposed the repository's RQ2/Event B labelling error, which we corrected in the synthesis. Claims were checked against code, outputs and tests.

= Threats to Validity

*Construct.* Coverage measures potential outward spread, not understanding, received knowledge or useful learning. A valid citation shows that a note was offered, not that the generated comment was correct.

*Internal.* Review end times omit exchanges during overlapping discussions, and we did not measure an alternative timing rule. Event A's activity cohorts and differing window populations prevent causal claims about turnover, and alternative-cutoff coverage was not measured. Event B's readability account is retrospective, and the Event A prediction's timing rests on the tracker.

*External.* RQ2 uses synthetic notes and queries on one network, with one seed, one retrieval limit and one embedding/generation configuration. The size of the gap may change with these choices.

*Conclusion and reliability.* Cached responses make the sampled generation run repeatable; fresh responses can differ even at temperature 0. CSV rounding, parsed-value agreement and compressed-file identity must also be distinguished.

= Conclusion

RQ1 recovers Trivago's reported range. Event A gives mixed support for the turnover predictions and shows the importance of activity and observation windows. Event B supports a small maintenance response while leaving research rationale to be documented. Under the selected RQ2 configuration, restricted sharing sharply reduces coverage, with a further reduction under generation. Preserving a checked baseline and isolating the sharing policy made these comparisons possible.
