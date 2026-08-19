# Thesis proposals

Three candidate topics. They are **alternatives, not components.** One gets built.

| | Topic | Status |
|---|---|---|
| [T1](T1/README.md) | Hardening-induced blind spots | Primary, gated behind the spike |
| [T2](T2/README.md) | Severity inversion in the Wazuh ruleset | Second fallback |
| [T3](T3/README.md) | Analytic robustness scoring | First fallback, has its own gate |

---

## The institutional template

Every proposal follows the same fixed structure. **Do not reorder or rename these sections.**

1. Area of Investigation (field and background)
2. Algorithms to be Used
3. Reasons for Choice of Project / The Current Process
4. Statement of the Problems (**exactly 5**)
5. Objectives of the Study: 1 general, then **exactly 5 specific**
6. Project Context (concept of the proposed system)
7. Features and Capabilities
8. System Modules (**exactly 5**)
9. Activity Diagram
10. Importance of the Study (**4 audiences**: society, the IT security industry, computer
    science as a discipline, security operations practitioners, plus future researchers)
11. Target Users
12. Similarities with any Previous Studies / Projects

## The numbering rule that is easy to break

Each specific objective is tagged to the problem it addresses, written inline as
`(addresses Problem N)`. Objective N answers Problem N.

If you add, remove, or reorder a problem, **every objective tag has to move with it.** This is
the single easiest thing to break when editing, and a panel will notice immediately.

## Prior work entries

Each entry under "Similarities with Previous Studies" gives, in this order:

1. Title, authors, year
2. Venue, and DOI or URL
3. What the study did, with **the concrete figures from the paper**, not a paraphrase
4. A separate paragraph: what this proposal does that the cited work did not

The concrete numbers matter. "They found many rules were evadable" is weak. "About half of
roughly 300 analyzed Windows process-creation Sigma rules" is what makes the citation load
bearing.

## Sourcing inside the proposals

- Engineering judgment is marked `(unverified)` inline. A labeled estimate is fine. An
  unlabeled guess is not.
- Numbers, dates, and any claim the reader may act on carry a source.
- **Do not soften the falsifiable claims.** T1 and T3 both pre-declare the result that would
  prove them wrong and commit to reporting a null result plainly. That is deliberate. It is
  the main defense against the sharpest objection a panel can raise.
