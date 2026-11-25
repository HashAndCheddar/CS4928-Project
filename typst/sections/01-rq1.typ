#import "../evidence.typ": ev, commit
= Introduction

Code review gives developers a way to discuss changes and share knowledge of a system. Dorner et al. model these exchanges as a communication network and estimate how far information could spread under favourable assumptions @study. We reproduce the Trivago range result, apply the method to Spotify activity windows, and examine how restricted sharing changes coverage @repo.

= Research Questions and Scope

*RQ1:* To what extent can the paper's Trivago diffusion range be reproduced using the authors' algorithm and dataset?

*RQ2:* How does retrieval-augmented memory affect diffusion coverage compared with perfect memory?

Both questions use the full Trivago network: 364 participants and 2,442 reviews. RQ2 adds synthetic notes, seed 0 and a limit of five items per member per review. The tracker records an RQ1 source-level coverage tolerance of $10^(-7)$, an expected maximum near 0.85, and RQ2 coverage equal to or slightly below perfect memory @tracker. No numerical threshold was defined for "slightly". The #commit("2e1b2ab12901a9a2bdb2d8f3376d4fc49c7886b0", [initial RQs]) (8 October) and the #commit("436ba8004cb0905e037ecf7bf1c811ee6039c26d", [bounded-sample plan]) (9 October) precede the #commit("da17616f4b7777ee0893f36d2352f2b89e2e523a", [M2 reproduction]) (20 October). The coordinator's frozen tracker copy (12 November) fixes the Event A entries and Week 9 decision before the Event B response (13 November) @trackerfrozen. The timing of the Event A prediction relative to its result rests on the tracker alone.

= RQ1 Method and Results

We used the authors' distance algorithm without modification. Reviews act as communication channels, and information can pass onward only through reviews with strictly later end times. Coverage for source $s$ is $C_s = abs(R_s) / N$: the number of other reachable participants divided by the full network population. Participants with zero reach remain in the distribution.

*Deviation.* The 9 October plan bounded the sample to the pack's first 12 participants in stable ID order. Trivago's size made the full network practical, so we ran all 364 sources; the 12 planned cases are a subset and lose nothing. Their reach ranges from 3 to 310 participants (median 265.5), so the frozen cases already show the spread that the full distribution summarises.

The #ev("research/rq1/run.py", [RQ1 runner]) regenerates distances and applies the authors' range calculation. Every row of the paper's Table 5 is reproduced at its reported precision @study (@tab:rq1). The median describes a typical participant; it differs from the lower bound of the paper's upper-70% interval.

#figure(
  table(columns: 4,
    table.header[*Top fraction*][*Paper*][*Ours*][*Other participants*],
    [0.7], [0.67-0.85], [0.67-0.85], [245-310],
    [0.5], [0.72-0.85], [0.72-0.85], [266-310],
    [0.3], [0.81-0.85], [0.81-0.85], [296-310],
    [0.1], [0.83-0.85], [0.83-0.85], [309-310],
    [Maximum], [0.85], [0.85], [310 / 364],
  ),
  caption: [Trivago normalized range, paper Tables 5-6 vs. reproduction. The median participant reaches 267 / 364 (0.73). Source: #ev("research/rq1/results/normalized_ranges.csv", [range output]).],
) <tab:rq1>

A later audit matched all 82,208 parsed distance rows against the public Trivago reference @dataset. Compressed-file bytes differed. CSV rounding also produces differences above $10^(-7)$ in cumulative probabilities, although matching the serialization recovers the saved values. These probabilities differ from source-level coverage; rounded paper tables alone cannot verify the tracker's tolerance. Validation used Python 3.12.14. The original environment was not reconstructed; commands and versions are recorded in the accompanying verification file.
