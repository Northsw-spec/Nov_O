"""CLI: local analysis only; never upload the copyrighted inputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .engine import load_ches_verse,reorder_verse
from .cvot import extract_bold_verses

def main():
    p=argparse.ArgumentParser(description='CHES word-order proposals checked against CVOT bold font')
    p.add_argument('--ches-zip',type=Path,required=True)
    p.add_argument('--cvot-pdf',type=Path,required=True)
    p.add_argument('--book',default='gen')
    p.add_argument('--chapter',type=int,default=1)
    p.add_argument('--page-start',type=int,default=19)
    p.add_argument('--page-end',type=int,default=21)
    p.add_argument('--verse-count',type=int,default=31)
    p.add_argument('--output',type=Path,default=Path('local_proposals.json'))
    a=p.parse_args()
    verses=extract_bold_verses(a.cvot_pdf,pages=(a.page_start,a.page_end),verse_count=a.verse_count,chapter_number=a.chapter)
    result={}
    for n in range(1,a.verse_count+1):
        ref=f'{a.book}.{a.chapter}.{n}'
        result[ref]=reorder_verse(load_ches_verse(a.ches_zip,ref),verses[n])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {len(result)} advisory proposals to {a.output}; '
          f'moved {sum(len(x["moves"]) for x in result.values())} CVOT-anchored groups')

if __name__=='__main__':
    main()
