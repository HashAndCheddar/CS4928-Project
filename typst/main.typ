// CS4928 Group Project – Final Synthesis
// Group G27, Project P28 (Dorner et al., Upper Bound of Information Diffusion in Code Review – Trivago)
// IEEE conference format, max 6 pages excluding references.
#import "ieee-local.typ": ieee

#show: ieee.with(
  // IEEE: one title line, no subtitle
  title: [G27: Reproducing the Upper Bound of Information Diffusion in Code Review at Trivago and Extending It with Retrieval-Augmented Memory],
  abstract: [
    We reproduce the Trivago information-diffusion range reported by Dorner et al.
    and compare perfect sharing with bounded retrieval and generation. The reproduction
    recovers a maximum reach of 310 other participants out of 364. A Spotify window
    comparison gives mixed support for turnover predictions. A separate maintenance
    exercise supports retaining the existing structure with a local clarification
    and boundary test. Under semantic top-5 retrieval, median coverage falls from
    0.73 to 0.04, and to 0.02 with generation. Bracketing the paper's timing rule with
    review start times moves median coverage between 0.48 and 0.88, so the
    reported bound is conditional on that rule. These findings are limited to the
    simulated information and recorded configurations.
  ],
  authors: (
    (
      name: "James Buckley",
      department: [Dept. of Computer Science and Information Systems],
      organization: [University of Limerick],
      location: [Limerick, Ireland],
      email: "23385812@studentmail.ul.ie",
    ),
    (
      name: "Adam Fox",
      department: [Dept. of Computer Science and Information Systems],
      organization: [University of Limerick],
      location: [Limerick, Ireland],
      email: "23368837@studentmail.ul.ie",
    ),
    (
      name: "Hersh Singh",
      department: [Dept. of Computer Science and Information Systems],
      organization: [University of Limerick],
      location: [Limerick, Ireland],
      email: "23371137@studentmail.ul.ie",
    ),
    (
      name: "Nathan Maher",
      department: [Dept. of Computer Science and Information Systems],
      organization: [University of Limerick],
      location: [Limerick, Ireland],
      email: "23370408@studentmail.ul.ie",
    ),
    (
      name: "Ben Curran",
      department: [Dept. of Computer Science and Information Systems],
      organization: [University of Limerick],
      location: [Limerick, Ireland],
      email: "23369205@studentmail.ul.ie",
    ),
  ),
  index-terms: (
    "code review",
    "information diffusion",
    "reproduction",
    "retrieval-augmented generation",
    "empirical software engineering",
  ),
  bibliography: bibliography("refs.bib"),
)

#include "sections/01-rq1.typ"
#include "sections/02-events-design.typ"
#include "sections/03-rq2-discussion.typ"
