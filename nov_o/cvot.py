"""Extract CVOT 2021 word-order hints solely from actual boldface font spans."""
from __future__ import annotations
from collections import defaultdict
import re
from pathlib import Path
WORD = re.compile(r"[A-Za-zÀ-ÿ]+(?:[-’'][A-Za-zÀ-ÿ]+)*")

def _lines(page):
    groups=defaultdict(list)
    for block in page.get_text('dict')['blocks']:
        if block.get('type') != 0:
            continue
        for line in block['lines']:
            for span in line['spans']:
                name,size,content=span['font'],span['size'],span['text']
                if not content.strip() or 'Supe' in name:
                    continue
                x0,y0,x1,y1=span['bbox']
                body=(11.5 <= size <= 14 and 'NewCaledonia' in name)
                verse_no=(7.9 <= size <= 9.0 and 'NewCaledonia' in name
                          and content.strip().isdigit() and len(content.strip()) <= 3)
                if not (body or verse_no) or y0 < 100 or y0 > 700:
                    continue
                groups[round(y0/3)*3].append((x0,y0,content,'Bold' in name,verse_no,size))
    result=[]
    for _,group in sorted(groups.items()):
        group.sort(key=lambda item:item[0])
        result.append(group)
    return result

def _words_from_fragments(fragments):
    chunks=[]
    for _,_,value,is_bold,_,_ in fragments:
        if is_bold:
            chunks.extend(WORD.findall(value.replace('ﬂ','fl').replace('ﬁ','fi')))
            if value.rstrip().endswith('-') and chunks:
                chunks[-1]+='-'
    return chunks

def _extend_words(target: list[str], words: list[str]) -> None:
    for word in words:
        if target and target[-1].endswith('-'):
            target[-1]=target[-1][:-1]+word
        else:
            target.append(word)

def extract_bold_verses(pdf_path: str | Path, *, pages: tuple[int,int],
                        verse_count: int, chapter_number: int = 1) -> dict[int,list[str]]:
    """Explicit 1-based page interval of a known chapter; fails on missing verses.

    chapter_number is the expected printed chapter marker, including chapters
    starting mid-page. Earlier chapter material is ignored. Do not use this as
    an all-book alignment or word-choice proof.
    """
    if chapter_number < 1 or verse_count < 1 or pages[0] < 1 or pages[1] < pages[0]:
        raise ValueError('invalid page range or verse count')
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError('Install PyMuPDF to inspect CVOT PDF') from exc
    with fitz.open(str(pdf_path)) as doc:
        if pages[1] > len(doc):
            raise ValueError('page range exceeds PDF')
        result={i:[] for i in range(1,verse_count+1)}
        current=0
        stop=False
        for page_index in range(pages[0]-1,pages[1]):
            for line in _lines(doc[page_index]):
                pending=[]
                for frag in line:
                    x,y,content,is_bold,is_small_num,size=frag
                    val=content.strip()
                    is_first=(current==0 and val==str(chapter_number) and is_bold
                              and not is_small_num and x<141
                              and 11.5<=size<=14)
                    if (current==verse_count and is_bold and x<141
                        and val.isdigit() and len(val)<=2):
                        stop=True
                        break
                    is_next=(is_small_num and val==str(current+1))
                    if (is_first or is_next) and current < verse_count:
                        if current and pending:
                            _extend_words(result[current],_words_from_fragments(pending))
                        current+=1
                        pending=[]
                    elif current and current <= verse_count:
                        pending.append(frag)
                if current and pending:
                    _extend_words(result[current],_words_from_fragments(pending))
                if stop:
                    break
            if stop:
                break
        missing=[n for n,v in result.items() if not v]
        if current!=verse_count or missing:
            raise ValueError(f'unverified CVOT verse extraction; final={current}, empty={missing}')
        return result
