import unittest
from nov_o.engine import reorder_verse

class WordOrderTests(unittest.TestCase):
    def test_verb_subject_swap_requires_cvot(self):
        out=reorder_verse(['in·beginning','he-created','Elohim','»','the·heavens'],
                          ['In','beginning','Elohim','created','heavens'])
        self.assertEqual([u['text'] for u in out['ordered_units']][:3],
                         ['in·beginning','Elohim','he-created'])
        self.assertEqual(out['status'],'PARTIAL')
        self.assertTrue(out['source_lexemes_preserved'])

    def test_conjunction_moved_without_loss(self):
        out=reorder_verse(['and·he-is-saying','Elohim','light'],
                          ['And','Elohim','said','light'])
        self.assertEqual([u['text'] for u in out['ordered_units']],
                         ['and','Elohim','he-is-saying','light'])
        self.assertEqual(out['ordered_units'][0]['source_spans'],[0])
        self.assertEqual(out['ordered_units'][2]['source_spans'],[0])

    def test_no_cvot_evidence_no_reorder(self):
        original=['and·he-is-saying','Elohim','light']
        out=reorder_verse(original,['No','usable','target'])
        self.assertEqual([u['text'] for u in out['ordered_units']],original)
        self.assertEqual(out['status'],'UNRESOLVED')

    def test_chapter_word_wrapping(self):
        out=reorder_verse(['and·he-is-','separating','Elohim'],['Elohim','separated'])
        self.assertEqual([u['text'] for u in out['ordered_units']],
                         ['and','Elohim','he-is-separating'])
        self.assertEqual(out['ordered_units'][2]['source_spans'],[0,1])

    def test_does_not_swap_unknown_noun(self):
        out=reorder_verse(['he-created','heaven'],['heaven','created'])
        self.assertEqual(out['status'],'UNRESOLVED')

if __name__=='__main__':
    unittest.main()
