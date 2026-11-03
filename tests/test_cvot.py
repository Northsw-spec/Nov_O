import unittest
from nov_o.cvot import _extend_words,_words_from_fragments

class CvotTokenTests(unittest.TestCase):
    def test_soft_line_hyphen_is_joined(self):
        target=[]
        _extend_words(target,_words_from_fragments([(0,0,'sepa-',True,False,12.7)]))
        _extend_words(target,_words_from_fragments([(0,0,'rated',True,False,12.7)]))
        self.assertEqual(target,['separated'])

    def test_roman_additions_excluded(self):
        spans=[(0,0,'In',True,False,12.7),
               (0,0,'a',False,False,12.7),
               (0,0,'beginning',True,False,12.7)]
        self.assertEqual(_words_from_fragments(spans),['In','beginning'])

if __name__=='__main__':
    unittest.main()
