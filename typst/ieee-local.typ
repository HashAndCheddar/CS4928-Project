// Adapted from charged-ieee 0.1.4 by Typst GmbH (MIT-0).
// https://github.com/typst/packages/tree/main/packages/preview/charged-ieee/0.1.4
// Keep the IEEE layout; inherit the compiler's installed default fonts.
#let ieee(title: [Paper Title], authors: (), abstract: none, index-terms: (), paper-size: "us-letter", bibliography: none, figure-supplement: [Fig.], body) = {
  set document(title: title, author: authors.map(author => author.name))
  set text(size: 10pt, spacing: .35em)
  set enum(numbering: "1)a)i)")
  show figure: set block(spacing: 15.5pt)
  show figure: set place(clearance: 15.5pt)
  show figure.where(kind: table): set figure.caption(position: top, separator: [\ ])
  show figure.where(kind: table): set text(size: 8pt)
  show figure.where(kind: table): set figure(numbering: "I")
  show figure.where(kind: image): set figure(supplement: figure-supplement, numbering: "1")
  show figure.caption: set text(size: 8pt)
  show figure.caption: set align(start)
  show figure.caption.where(kind: table): set align(center)
  set figure.caption(separator: [. ])
  show figure: fig => {
    let prefix = if fig.kind == table [TABLE] else if fig.kind == image [Fig.] else [#fig.supplement]
    let numbers = numbering(fig.numbering, ..fig.counter.at(fig.location()))
    show figure.caption: it => block[#prefix~#numbers#it.separator#it.body]
    show figure.caption.where(kind: table): smallcaps
    fig
  }
  show raw: set text(ligatures: false, size: 0.85em, spacing: 100%)
  set columns(gutter: 12pt)
  set page(columns: 2, paper: paper-size, margin: if paper-size == "a4" {
    (x: 41.5pt, top: 80.51pt, bottom: 89.51pt)
  } else {
    (x: (50pt / 216mm) * 100%, top: (55pt / 279mm) * 100%, bottom: (64pt / 279mm) * 100%)
  })
  set math.equation(numbering: "(1)")
  show math.equation: set block(spacing: 0.65em)
  show ref: it => {
    if it.element != none and it.element.func() == math.equation {
      link(it.element.location(), numbering(it.element.numbering, ..counter(math.equation).at(it.element.location())))
    } else { it }
  }
  set enum(indent: 10pt, body-indent: 9pt)
  set list(indent: 10pt, body-indent: 9pt)
  set heading(numbering: "I.A.a)")
  show heading: it => {
    let levels = counter(heading).get()
    let deepest = if levels != () { levels.last() } else { 1 }
    set text(10pt, weight: 400)
    if it.level == 1 {
      let is-ack = it.body in ([Acknowledgment], [Acknowledgement], [Acknowledgments], [Acknowledgements])
      set align(center)
      set text(if is-ack { 10pt } else { 11pt })
      show: block.with(above: 15pt, below: 13.75pt, sticky: true)
      show: smallcaps
      if it.numbering != none and not is-ack { numbering("I.", deepest); h(7pt, weak: true) }
      it.body
    } else if it.level == 2 {
      set text(style: "italic")
      show: block.with(spacing: 10pt, sticky: true)
      if it.numbering != none { numbering("A.", deepest); h(7pt, weak: true) }
      it.body
    } else [
      #if it.level == 3 { numbering("a)", deepest); [ ] }
      _#(it.body):_
    ]
  }
  show std.bibliography: set text(8pt)
  show std.bibliography: set block(spacing: 0.5em)
  set std.bibliography(title: text(10pt)[References], style: "ieee")
  place(top, float: true, scope: "parent", clearance: 30pt, {
    {
      set align(center)
      set par(leading: 0.5em)
      set text(size: 24pt)
      block(below: 8.35mm, title)
    }
    set par(leading: 0.6em)
    for i in range(calc.ceil(authors.len() / 3)) {
      let end = calc.min((i + 1) * 3, authors.len())
      let slice = authors.slice(i * 3, end)
      grid(columns: slice.len() * (1fr,), gutter: 12pt, ..slice.map(author => align(center, {
        text(size: 11pt, author.name)
        if "department" in author [\ #emph(author.department)]
        if "organization" in author [\ #emph(author.organization)]
        if "location" in author [\ #author.location]
        if "email" in author {
          if type(author.email) == str [\ #link("mailto:" + author.email)] else [\ #author.email]
        }
      })))
      if end != authors.len() { v(16pt, weak: true) }
    }
  })
  set par(justify: true, first-line-indent: (amount: 1em, all: true), spacing: 0.5em, leading: 0.5em)
  if abstract != none {
    set par(spacing: 0.45em, leading: 0.45em)
    set text(9pt, weight: 700, spacing: 150%)
    [_Abstract_---#h(weak: true, 0pt)#abstract]
    if index-terms != () { parbreak(); [_Index Terms_---#h(weak: true, 0pt)#index-terms.join[, ]] }
    v(2pt)
  }
  body
  if bibliography != none { block(breakable: false, bibliography) }
}
