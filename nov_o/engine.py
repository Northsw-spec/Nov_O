"""CHES source-preserving local word-order reorderer (CVOT boldface-anchored)."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json
import re
import zipfile

IRREGULAR = {'said':'say','saw':'see','made':'make','came':'come',
             'was':'be','were':'be','is':'be','are':'be','has':'have',
             'given':'give','gave':'give','taken':'take','took':'take',
             'created':'create','separated':'separate','called':'call'}
PRONOUN_PREFIX = re.compile(r'^(?:he|she|they|we|you|i)-(?:is-|are-|was-|were-|shall-|will-|have-|has-)?', re.I)
MARKERS = frozenset({'»','(p)','c','m','s','d','!','¶'})
WORD = re.compile(r'[a-z]+')

@dataclass(frozen=True)
class Unit:
    raw: str
    sources: tuple[int, ...]

def load_ches_verse(archive: str | Path, ref: str) -> list[str]:
    match = re.fullmatch(r'([a-z0-9]{2,4})\.([1-9]\d*)\.([1-9]\d*)', ref)
    if not match:
        raise ValueError('expected e.g. gen.1.3')
    book, chapter, _verse = match.groups()
    key = f'ches/{book}.{chapter}.json'
    with zipfile.ZipFile(archive) as z:
        if key not in z.namelist():
            raise KeyError(f'chapter absent: {key}')
        if z.getinfo(key).file_size > 5_000_000:
            raise ValueError('CHES chapter over safety limit')
        root = json.loads(z.read(key))
    if root.get('book') != book or root.get('chapter') != int(chapter):
        raise ValueError('CHES chapter identity mismatch')
    for item in root['verses']:
        if item['reference'] == ref:
            return [span['original_ches_line_text'] for span in item['source_ches_spans_NOT_OLT_TRANSLATION']]
    raise KeyError(f'unknown verse {ref}')

def _stems(word: str) -> set[str]:
    w = WORD.findall(word.lower().replace('ﬂ','fl').replace('ﬁ','fi'))
    if not w:
        return set()
    w = w[-1]
    forms = {w, IRREGULAR.get(w,w)}
    if w.endswith('ing') and len(w)>5:
        root=w[:-3]
        forms.update((root,root+'e'))
        if root.endswith(root[-1]*2):
            forms.add(root[:-1])
    if w.endswith('ed') and len(w)>4:
        forms.update((w[:-2],w[:-1]))
    if w.endswith('s') and len(w)>3:
        forms.add(w[:-1])
    return forms

def _verb_root(raw: str) -> set[str]:
    s=raw.lower().replace('·','-')
    if s.startswith('and-'):
        s=s[4:]
    if not PRONOUN_PREFIX.match(s):
        return set()
    s=PRONOUN_PREFIX.sub('',s,count=1).strip('-')
    if not s or s in ('not','be'):
        return set()
    return _stems(s)

def _join_wrapped(raw: list[str]) -> list[Unit]:
    """Join visibly hyphen-ended PDF spans, retaining source IDs."""
    units=[]
    i=0
    while i<len(raw):
        val=raw[i]; sources=[i]
        while val.endswith('-') and i+1<len(raw) and re.match(r'^[a-z]',raw[i+1]):
            i+=1
            val+=raw[i]; sources.append(i)
        units.append(Unit(val,tuple(sources)))
        i+=1
    return units

def _subject(window: list[Unit]) -> int:
    if not window:
        return 0
    first=window[0].raw
    if first.lower() in ('elohim','yahweh','adam','moses'):
        if first.lower()=='yahweh' and len(window)>1 and window[1].raw.lower()=='elohim':
            return 2
        return 1
    if re.fullmatch(r'(?:the·)?[A-Za-z]+(?:-[A-Za-z]+)*',first):
        return 1 if first.startswith('the·') else 0
    return 0

def _cvot_orders_subject_before_verb(subject: list[Unit], verb: Unit,
                                    bold_words: list[str], used: set[int]) -> int | None:
    roots=_verb_root(verb.raw)
    if not roots:
        return None
    subparts=[]
    for u in subject:
        subparts.extend(WORD.findall(u.raw.lower().replace('·',' ')))
    if not subparts:
        return None
    target=[w.lower() for w in bold_words]
    for i in range(len(target)-len(subparts)):
        if i in used or target[i:i+len(subparts)] != subparts:
            continue
        tail=target[i+len(subparts):i+len(subparts)+4]
        if any(_stems(w) & roots for w in tail):
            return i
    return None


def _anchor_order_consistent(source_index: int, cvot_position: int,
                             moves: list[dict]) -> bool:
    """Do not cross source/target clause anchor orders."""
    for m in moves:
        src = min(m['source_verb_indices'])
        target = m['cvot_bold_subject_index']
        if src == source_index or (src < source_index) != (target < cvot_position):
            return False
    return True


def _cvot_svo_object_anchor(subject: list[Unit], verb: Unit, obj: Unit,
                            bold_words: list[str], used: set[int]) -> int | None:
    """Recognize only CHES direct or prepositional THEM, not unknown objects."""
    if obj.raw == '»·them':
        object_words = ['them']
    elif obj.raw == 'to·them':
        object_words = ['to', 'them']
    else:
        return None
    roots = _verb_root(verb.raw)
    if not roots:
        return None
    subject_words = [w for u in subject
                     for w in WORD.findall(u.raw.lower().replace('·', ' '))]
    if not subject_words:
        return None
    target = [w.lower() for w in bold_words]
    minimum = len(subject_words) + 1 + len(object_words)
    for start in range(len(target) - minimum + 1):
        if start in used or target[start:start+len(subject_words)] != subject_words:
            continue
        vi = start + len(subject_words)
        if (_stems(target[vi]) & roots) and target[vi+1:vi+1+len(object_words)] == object_words:
            return start
    return None


def _move_object_before_subject(units: list[Unit], bold_words: list[str],
                                used: set[int], prior_moves: list[dict]
                                ) -> tuple[list[Unit], list[dict]]:
    """Move narrowly attested V-O-S to S-V-O, retaining original source IDs."""
    out: list[Unit] = []
    changes: list[dict] = []
    i = 0
    while i < len(units):
        if i + 2 < len(units):
            verb, obj, subj = units[i:i+3]
            if _subject([subj]) == 1:
                anchor = _cvot_svo_object_anchor([subj], verb, obj, bold_words, used)
                if anchor is not None and _anchor_order_consistent(
                    min(verb.sources), anchor, prior_moves + changes
                ):
                    if verb.raw.startswith('and·'):
                        out.append(Unit('and',verb.sources))
                        moving_verb = Unit(verb.raw[4:],verb.sources)
                    else:
                        moving_verb = verb
                    out.extend((subj,moving_verb,obj))
                    changes.append({
                        'source_verb_indices':list(verb.sources),
                        'subject_source_indices':[list(subj.sources)],
                        'object_source_indices':list(obj.sources),
                        'rule':'VOS_TO_SVO_CVOT_BOLD_OBJECT_ANCHORED',
                        'cvot_bold_subject_index':anchor,
                    })
                    used.add(anchor)
                    i += 3
                    continue
        out.append(units[i])
        i += 1
    return out,changes

def reorder_verse(ches_spans: list[str], cvot_bold_words: list[str]) -> dict:
    """Advisory local VSO->SVO proposal only; no entire-verse PASS is possible."""
    if not isinstance(ches_spans,list) or not all(isinstance(x,str) for x in ches_spans):
        raise TypeError('CHES spans must be a list of strings')
    if not isinstance(cvot_bold_words,list) or not all(isinstance(x,str) for x in cvot_bold_words):
        raise TypeError('CVOT words must be a list of strings')
    units=_join_wrapped(ches_spans)
    proposed=[]; moves=[]; used_target_positions=set(); i=0
    while i<len(units):
        candidate=units[i]
        roots=_verb_root(candidate.raw)
        subject_len=_subject(units[i+1:i+3]) if roots else 0
        subject=units[i+1:i+1+subject_len]
        target_position=(_cvot_orders_subject_before_verb(subject,candidate,cvot_bold_words,used_target_positions)
                         if subject_len else None)
        if target_position is not None and _anchor_order_consistent(
            min(candidate.sources), target_position, moves
        ):
            if candidate.raw.startswith('and·'):
                proposed.append(Unit('and',candidate.sources))
                verb=Unit(candidate.raw[4:],candidate.sources)
            else:
                verb=candidate
            proposed.extend(subject); proposed.append(verb)
            moves.append({'source_verb_indices':list(candidate.sources),
                          'subject_source_indices':[list(s.sources) for s in subject],
                          'rule':'VSO_TO_SVO_CVOT_BOLD_ANCHORED',
                          'cvot_bold_subject_index':target_position})
            used_target_positions.add(target_position)
            i+=1+subject_len
        else:
            proposed.append(candidate); i+=1
    proposed, object_moves = _move_object_before_subject(
        proposed, cvot_bold_words, used_target_positions, moves
    )
    moves.extend(object_moves)
    def atoms(values):
        return Counter(a for v in values for a in v.raw.replace('·','-').split('-') if a)
    if atoms(units) != atoms(proposed):
        raise ValueError('CHES source lexemes changed; refusing proposal')
    if {n for u in proposed for n in u.sources} != set(range(len(ches_spans))):
        raise ValueError('CHES source span coverage changed; refusing proposal')
    english_units=[{'text':u.raw,'source_spans':list(u.sources)} for u in proposed
                   if u.raw.lower() not in MARKERS]
    readable=re.sub(r'\s+', ' ', ' '.join(x['text'].replace('»','').replace('·',' ')
                                      for x in english_units)).strip()
    return {'status':'PARTIAL' if moves else 'UNRESOLVED',
            'proposal_only':True,'ches_original_spans':ches_spans,
            'ordered_units':[{'text':u.raw,'source_spans':list(u.sources)} for u in proposed],
            'english_word_order':readable,
            'moves':moves,'source_lexemes_preserved':True,
            'source_spans_preserved':True,'cvot_anchor_order_preserved':True,
            'cvot_bold_word_count':len(cvot_bold_words)}
