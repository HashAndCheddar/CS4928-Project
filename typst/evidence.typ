// Evidence URLs refer to the repository state inspected on 20 November 2026.
#let repo = "https://github.com/HashAndCheddar/CS4928-Project"
#let state = "40f8c8556f11cbc9d8e38a7cd3aac6b12a0adb20"
#let ev(path, label, ref: state) = link(repo + "/blob/" + ref + "/" + path, label)
#let commit(ref, label) = link(repo + "/commit/" + ref, label)
#let comparison = link(repo + "/compare/a3704ea1b5cf30a513b0e945af55613de8c248a7...c936f52cc02d0e0b5f2d70d87df29ea71233195a")[maintenance diff]
