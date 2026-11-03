# Nov_O — CHES/CVOT word-order prototype

**Status: experimental, local-data-only. No final verse has been approved.**

This repository implements a conservative English word-order proposal engine. The user-supplied CHES JSON archive is the source of English words; the user-supplied CVOT 2021 PDF supplies **word-order evidence from its actual bold font**, not replacement English words. Lightface CVOT additions are excluded. The publisher's description distinguishes Hebrew-counterpart boldface from explanatory lightface.

## Scope implemented

- Load specific CHES source spans and retain original source-span indices.
- Read an **explicitly supplied CVOT PDF page range**; extract boldface words, excluding headers, superscripts, footnotes and lightface words.
- Handle some hyphenated words split across PDF lines.
- Propose a strictly local **verb–subject to subject–verb** reorder when a matching CVOT bold subject–verb sequence supports the move.
- Split bound CHES conjunction `and·` only for an evidenced move. Retain all original CHES spans, including markers, in the JSON audit record.
- Preserve a multiset of original source lexical atoms; fail if they change. Mark proposals `PARTIAL` or `UNRESOLVED`, never overall PASS.

## Local usage

Python 3.12+ and the optional PDF reader package:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m nov_o --ches-zip '/path/to/ches.zip' --cvot-pdf '/path/to/CVOT-2021.pdf' --book gen --chapter 1 --page-start 19 --page-end 21 --verse-count 31 --output local_proposals.json
```

The defaults apply **only to Genesis 1 in the inspected 2021 PDF**. The tool does **not** yet locate all other chapters, establish all lexical correspondences, or prove complete English grammar. It needs verified page boundaries for each other chapter. Unmatched structures are left unchanged. `english_word_order` is an unapproved display preview and may remain awkward or partly interlinear.

## Limitations and provenance

The supplied archive contains individual PDF-derived spans, not a independently verified one-to-one Hebrew lexical alignment. CHES and CVOT sometimes choose different English lexemes. A CVOT word-order anchor alone does not license replacing a CHES expression. Variants, phrase roles, multiple related clauses, pronouns, tenses and whole-verse grammatical correctness require separate work and independent review.

**Do not commit the original CHES ZIP, the CVOT PDF, or output chapter text.** Source redistribution rights have not been established. The .gitignore covers common local input/output formats. GitHub Actions tests use synthetic examples and do not certify the corpus.

## Next work

Build audited verse-level token alignment and more robust CHES PDF-fragment reconstruction; independently verify representative cases from other books; add clause/phrase constraints; measure failure rates before broadening beyond locally proven movements.

## Stage 2: constrained object-subject ordering

In addition to the original verb-subject swap, the engine can now propose a verb-object-subject to subject-verb-object permutation for the literal CHES object forms »·them and to·them, only where the CVOT boldface sequence independently supports the subject, verb root and object order. It does not generalize to other objects. Source-span completeness, lexeme multiset equality, non-reused CVOT anchors and noncrossing clause-anchor order are enforced. The original source documents remain outside the repository.

An offline audit of uploaded Genesis 1 data found 29 individually anchored moves (26 original VSO, 3 new VOS) across 24 of 31 verses; 7 verses had no movement. These are mechanical proposals, not full grammatical validation. See docs/verification/GENESIS_1_LOCAL_AUDIT.md.


## Genesis 2–3: chapter-aware PDF extraction

The CVOT reader now accepts an explicit chapter_number (default 1 for backwards compatibility), so it can start at a **mid-page** chapter marker instead of silently reading the preceding chapter. Both chapter and verse markers must have the expected PDF typography; missing sequential markers fail closed. The CLI forwards --chapter to the reader.

Locally verified page intervals for the supplied CVOT 2021 PDF:
- Genesis 1: --chapter 1 --page-start 19 --page-end 21 --verse-count 31
- Genesis 2: --chapter 2 --page-start 21 --page-end 23 --verse-count 25
- Genesis 3: --chapter 3 --page-start 23 --page-end 25 --verse-count 24

A limited offline audit found 11 CVOT-anchored VSO moves in Genesis 2 and 11 in Genesis 3, with original CHES words preserved. These are **partial local word-order proposals**, not completed verse translations. See docs/verification/GENESIS_2_3_LOCAL_AUDIT.md. Source documents and generated chapter text remain local.
