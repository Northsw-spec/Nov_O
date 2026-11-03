# Genesis 2–3: local chapter-boundary and word-order audit (2026-11-03)

## Input identity, verified offline
- CHES ZIP SHA-256: 5bdd72e7b193470e2700eb51a2fd417c2e7942248425ee4e17c5565d21aa11a7
- CVOT 2021 PDF SHA-256: c7f46321e54346661b62add24df12f1ce8e8fd56535227723975c0b0879470ed
- CHES chapter paths: ches/gen.2.json and ches/gen.3.json
- CVOT Genesis 2 begins after Genesis 1 on PDF page 21 and ends before Genesis 3 on PDF page 23; Genesis 3 ends on page 25.
- Actual font metadata and rendered PDF pages 21 and 23 inspected. Chapter markers use body-sized bold NewCaledonia; verse markers use smaller NewCaledonia.

## Before fix
Calling the previous extractor for Genesis 2 with pages 21–23 and verse_count 25 failed with final=0, because it hardcoded the first chapter marker as "1" instead of "2". Genesis 3 also failed.

## After fix — local original-file run
- Genesis 1, pages 19–21, 31/31 verses: still extracts successfully (regression).
- Genesis 2, pages 21–23, 25/25 verses, 377 CHES source spans: 11 local VSO→SVO proposals across 10 verses; 15 verses with no moves.
- Genesis 3, pages 23–25, 24/24 verses, 415 CHES source spans: 11 local VSO→SVO proposals across 10 verses; 14 verses with no moves.
- These proposals preserve original CHES material and original source-span indices in the current engine; no CHES lexical substitution.
- The standalone CLI passes the explicit chapter number to the PDF reader. Example (with local, licensed files only):

    python -m nov_o --ches-zip /path/to/ches.zip --cvot-pdf /path/to/CVOT-2021.pdf --book gen --chapter 2 --page-start 21 --page-end 23 --verse-count 25 --output local_gen2_proposals.json

- Synthetic tests model previous-chapter text, a mid-page chapter header, split-page continuation, next-chapter text, font-weight isolation and missing verse markers.

## Cautions and open issues
These are **proposals**, not proof that an entire verse is grammatical or that Hebrew-source alignment is correct. The font extractor depends on layout and does not yet generalize to other PDF editions. It may still miss source/target ambiguities, tricky verse numbering, or more complex clauses. It does not itself verify the biblical syntax beyond small anchored patterns. The full-source original inputs and locally generated verse outputs are not committed.

Keep PR #1 draft and require exact-head green GitHub-hosted Ubuntu foundation checks before any review/merge.
