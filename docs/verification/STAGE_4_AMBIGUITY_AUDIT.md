# Stage 4: abstain on ambiguous CVOT anchors and interrupted names

Local source audit date: 2026-11-03.

The user-supplied CHES ZIP and CVOT PDF revealed two concrete risks:
- Genesis 1:27 contains more than one matching CVOT boldface subject/verb position. Choosing the first would be unverified clause alignment.
- Genesis 3:1 has an editorial marker between Yahweh and Elohim in CHES. Moving only Yahweh splits the proper-name phrase. Such a move is now blocked.

The same unique-position requirement also applies to supported VOS subject/verb/object moves. Adjacent Yahweh Elohim is still treated as a two-unit subject. CHES word choices, original span IDs and source markers are conserved.

## Validation

Three of the six newly frozen synthetic cases failed on the previous version, as intended. All 27 local synthetic tests passed on the corrected engine. The original source files were also checked offline with the exact same chapter/page definitions used in earlier audits.

| Chapter | Previous candidate moves | Revised candidate moves | Changed verses |
| --- | ---: | ---: | ---: |
| Genesis 1 | 29 | 28 | 23 / 31 |
| Genesis 2 | 11 | 11 | 10 / 25 |
| Genesis 3 | 11 | 10 | 10 / 24 |
| Total | 51 | 49 | 43 / 80 |

These numbers count individual mechanical proposals, not approved complete translations. No full CHES/CVOT text or generated chapter verses are committed to this public repository. Source HASHES remain as documented in the earlier audits. Syntactic validation, clause identity and complete English grammar remain unresolved.
