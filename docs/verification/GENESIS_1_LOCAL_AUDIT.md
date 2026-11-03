# Genesis 1 offline source audit — 2026-11-03

## Inputs, identified by SHA-256 only
- Uploaded CHES ZIP: 5bdd72e7b193470e2700eb51a2fd417c2e7942248425ee4e17c5565d21aa11a7
- Uploaded CVOT 2021 PDF: c7f46321e54346661b62add24df12f1ce8e8fd56535227723975c0b0879470ed
- CVOT PDF pages 19–21; original NewCaledonia-Bold font metadata; regular font and superscripts excluded
- CHES: 31 Genesis 1 verse records, 526 original spans

## Local deterministic results
- 26 CVOT-anchored verb-subject to subject-verb moves.
- 3 additional CVOT-anchored verb-object-subject to subject-verb-object moves.
- 29 moves in 24 verses; 7 verses unchanged.
- Original CHES span IDs and lexical atoms preserved across every move.
- Genesis 1:22: one new object-aware move; Genesis 1:28: two such moves.
- Genesis 1:17: untouched. CHES and CVOT use different verbs there; no synonym is inferred.

## Fail-closed rules
No target anchor, conflicting word order, unrecognized object, mismatching verb root, anchor reuse or crossed clause anchors means no move. A source atom mismatch or lost source span raises ValueError.

## Limitations
These counts are NOT a whole-verse quality score, independently verified Hebrew correspondence, approval of translated text or permission to publish a derivative corpus. The English preview is incomplete and retains interlinear features. PDF-derived CHES spans may include fragments and grammatical annotation, and other chapters need independent verified page bounds. CI uses synthetic fixtures only; copyrighted original inputs and full generated chapter texts are not committed.

Keep PR #1 in draft until the updated exact-head foundation job passes and further source-level review is completed.
