#import "../evidence.typ": ev, commit
= Introduction

Code review gives developers a way to discuss changes and share knowledge of a system. Dorner et al. model these exchanges as a communication network and estimate how far information could spread under favourable assumptions @study. We reproduce the Trivago range result, apply the method to Spotify activity windows, and examine how restricted sharing changes coverage @repo.

= Research Questions and Scope

*RQ1:* To what extent can the paper's Trivago diffusion range be reproduced using the authors' algorithm and dataset?

*RQ2:* How does retrieval-augmented memory affect diffusion coverage compared with perfect memory?

Both questions use the full Trivago network: 364 participants and 2,442 reviews. RQ2 adds synthetic notes, seed 0 and a limit of five items per member per review. The tracker records an RQ1 source-level coverage tolerance of $10^(-7)$, an expected maximum near 0.85, and RQ2 coverage equal to or slightly below perfect memory @tracker. No numerical threshold was defined for "slightly". The #commit("2e1b2ab12901a9a2bdb2d8f3376d4fc49c7886b0", [initial RQs]) precede the #commit("da17616f4b7777ee0893f36d2352f2b89e2e523a", [M2 reproduction]). Complete freeze and prediction histories were unavailable.

= RQ1 Method and Results

We used the authors' distance algorithm without modification. Reviews act as communication channels, and information can pass onward only through reviews with strictly later end times. Coverage for source $s$ is $C_s = abs(R_s) / N$: the number of other reachable participants divided by the full network population. Participants with zero reach remain in the distribution.

Trivago's size made the bounded reproduction practical without sampling. The #ev("research/rq1/run.py", [RQ1 runner]) regenerates distances and applies the authors' range calculation. The results agree with the paper at its reported precision @study. The median describes a typical participant; it differs from the lower bound of the paper's upper-70% interval.

#figure(
  table(columns: 3,
    table.header[*Measure*][*Other participants*][*Coverage*],
    [Maximum], [310 / 364], [0.85],
    [Median], [267 / 364], [0.73],
    [Upper 70% interval], [245-310], [0.67-0.85],
  ),
  caption: [Trivago diffusion range. Source: #ev("research/rq1/results/normalized_ranges.csv", [range output]).],
) <tab:rq1>

A later audit matched all 82,208 parsed distance rows against the public Trivago reference @dataset. Compressed-file bytes differed. CSV rounding also produces differences above $10^(-7)$ in cumulative probabilities, although matching the serialization recovers the saved values. These probabilities differ from source-level coverage; rounded paper tables alone cannot verify the tracker's tolerance. Validation used Python 3.12.14. The original environment was not reconstructed; commands and versions are recorded in the accompanying verification file.
