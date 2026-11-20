#import "../evidence.typ": ev, commit, comparison
= Change Event A

Event A applies the same coverage measure to Spotify's 3 February-1 March 2020 network: 1,730 participants and 22,504 reviews @eventabrief. We split reviews by end time into 3-16 February and 17 February-1 March. The early/late turnover comparison is new; the authors' full-month Spotify results were already available.

We predicted that experienced participants leaving would lower late median coverage, and that newcomers would have lower late coverage than continuing participants. Continuing, left and joined denote activity in both windows, early only and late only. Experience means the top quarter of early participants by review activity. These labels describe activity, not employment.

The #ev("research/event_a/run.py", [runner]) retains the M2 algorithm and timing rule. Coverage uses each window's active population as its denominator. The #ev("research/event_a/results/turnover.csv", [cohort results]) and #ev("research/event_a/results/normalized_ranges.csv", [range distributions]) support the comparison.

#figure(
  image("../figures/event-a-coverage.svg", width: 100%),
  caption: [Spotify median coverage by window and late-window cohort. Values use the relevant window's active population as denominator; $n$ gives the window or cohort size.],
) <fig:event-a>

The first prediction is challenged: median coverage rises from 0.10 to 0.46 despite three experienced early-only participants. The second is supported descriptively: newcomers have median coverage 0.02, compared with 0.50 for continuing participants. Full-month Spotify matches Trivago's rounded maximum of 0.85 and median of 0.73, but the shorter windows have maxima of 0.65 and 0.76. The method transfers; the full-month result depends on the observation window.

The late window has 32% more reviews. Changes in activity, population and available diffusion time prevent a causal conclusion about turnover. Low outward reach also says little about the information newcomers receive. The design implication is to document module decisions and maintenance rules explicitly, reducing reliance on review history. An onboarding benefit was not measured.

= Software Design Decision

Review end times omit exchanges that may occur during overlapping discussions. We compared retaining this rule, using start/end intervals, and using comment or approval timestamps. The original rule preserves comparability and requires no extra data. Intervals capture overlap but need a transfer-time assumption. Interaction timestamps offer finer detail but require suitable data and a larger modelling change.

We retained end times for RQ1 and Event A. The #ev("simulation/model.py", [loader]) and #ev("simulation/minimal_distances.py", [path algorithm]) implement the paper's rule @study. This keeps the comparison controlled and limits verification work, at the cost of timing realism. We did not measure an alternative timing model.

= Change Event B

Event B concerns maintenance by a contributor without prior review involvement @eventbbrief. We examined the dataset/window walkthrough and split-cutoff exercise, comparing #commit("c936f52cc02d0e0b5f2d70d87df29ea71233195a", [response c936f52]) with its parent #commit("a3704ea1b5cf30a513b0e945af55613de8c248a7", [a3704ea]). The historical account expected a local change without redesign. The contributor later reported that the code and reports were readable, but retained no walkthrough notes or timings. This is a retrospective account; the exact M4 freeze and prediction dates remain unverified.

We considered no change, a local clarification and boundary test, or a general dataset/window interface. No change leaves the relevant rules implicit. A general interface adds flexibility and indirection beyond this task's needs. We chose the clarification and test, retaining the existing structure.

#figure(
  table(columns: (1fr, 1.6fr),
    table.header[*Area*][*Change*],
    [Dataset and dates], [One comment at the Spotify load; production logic unchanged.],
    [Window boundary], [A new 34-line test checks start inclusion, split assigned to late only, end exclusion and disjoint windows.],
    [Results], [Original cutoff and coverage outputs retained.],
  ),
  caption: [Maintenance response: #comparison and #ev("test/test_event_a.py", [boundary test], ref: "c936f52cc02d0e0b5f2d70d87df29ea71233195a").],
) <tab:event-b>

The #ev("research/event_a/results/split_sensitivity.csv", [split-count analysis]) moves the cutoff from 17 to 18 February. This reassigns 973 reviews: early/late counts change from 9,703/12,801 to 10,676/11,828, while the total remains 22,504. Continuing/left/joined counts change from 1,397/131/202 to 1,402/145/183. Coverage was not recomputed for these alternative cutoffs.

The response supports retaining the simple structure for these local changes. The comment exposes the dataset/date dependency, and the test makes the boundary rule explicit. A newcomer still needs the research rationale for selecting a dataset and window. Comments can become stale, tests need maintenance, and the timing assumption remains unvalidated. RQ2 is reported separately because its earlier Event B label does not match the official task.
