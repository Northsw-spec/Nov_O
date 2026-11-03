"""Synthetic chapter-boundary tests; never include or distribute the CVOT PDF."""
from __future__ import annotations
import sys
import unittest
from unittest.mock import patch
from nov_o import cvot

def fragment(value: str, *, x: float = 135.5, bold: bool = True, small: bool = False):
    return (x,215.0,value,bold,small,8.27 if small else 12.73)

class FakePDF:
    def __init__(self, page_count: int):
        self.page_count=page_count
    def __enter__(self):
        return self
    def __exit__(self,*args):
        return None
    def __len__(self):
        return self.page_count
    def __getitem__(self,i):
        return i

class ChapterBoundaryTests(unittest.TestCase):
    def extract(self, lines_by_page, *, chapter=2, count=3):
        fake=type('FakeFitz',(),{'open':staticmethod(lambda _file:FakePDF(len(lines_by_page)))})
        with patch.dict(sys.modules,{'fitz':fake}):
            with patch.object(cvot,'_lines',side_effect=lines_by_page):
                return cvot.extract_bold_verses('synthetic-not-an-actual-pdf',
                    pages=(1,len(lines_by_page)),verse_count=count,chapter_number=chapter)

    def test_skips_previous_chapter_and_stops_at_next(self):
        pages=[
            [[fragment('31',small=True),fragment('OLD_PREVIOUS_CHAPTER')],
             [fragment('2',x=122.7),fragment('first')],
             [fragment('2',small=True),fragment('second')]],
            [[fragment('third')],
             [fragment('3',small=True),fragment('third_verse')],
             [fragment('3',x=122.7),fragment('NEXT_CHAPTER')]]
        ]
        result=self.extract(pages)
        self.assertEqual(result,{1:['first'],2:['second','third'],3:['third','verse']})
        all_words=sum(result.values(),[])
        self.assertNotIn('OLD_PREVIOUS_CHAPTER',all_words)
        self.assertNotIn('NEXT_CHAPTER',all_words)

    def test_chapter_one_backward_compatibility(self):
        pages=[[[fragment('1',x=122.7),fragment('initial')],
                [fragment('2',small=True),fragment('next')],
                [fragment('3',x=122.7),fragment('future')]]]
        self.assertEqual(self.extract(pages,chapter=1,count=2),
                         {1:['initial'],2:['next']})

    def test_wrong_chapter_fails_closed(self):
        pages=[[[fragment('2',x=122.7),fragment('initial')],
                [fragment('2',small=True),fragment('next')]]]
        with self.assertRaisesRegex(ValueError,'unverified CVOT'):
            self.extract(pages,chapter=3,count=2)

    def test_missing_sequential_verse_fails_closed(self):
        pages=[[[fragment('2',x=122.7),fragment('first')],
                [fragment('3',small=True),fragment('skipped_second')]]]
        with self.assertRaisesRegex(ValueError,'unverified CVOT'):
            self.extract(pages,chapter=2,count=3)

    def test_regular_text_excluded(self):
        pages=[[[fragment('2',x=122.7),fragment('Only'),fragment('added',bold=False)],
                [fragment('2',small=True),fragment('bold'),fragment('light',bold=False)]]]
        self.assertEqual(self.extract(pages,chapter=2,count=2),
                         {1:['Only'],2:['bold']})

    def test_chapter_zero_rejected(self):
        pages=[[[fragment('1',x=122.7),fragment('start')]]]
        with self.assertRaises(ValueError):
            self.extract(pages,chapter=0,count=1)

if __name__=='__main__':
    unittest.main()
