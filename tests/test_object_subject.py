"""Synthetic CI fixtures; original CHES/CVOT documents are never uploaded."""
import unittest
from nov_o.engine import reorder_verse

class ObjectSubjectTests(unittest.TestCase):
    def test_vos_direct_object(self):
        out=reorder_verse(['and·he-is-','blessing','»·them','Elohim'],
                          ['And','Elohim','blessed','them'])
        self.assertEqual([u['text'] for u in out['ordered_units']],
                         ['and','Elohim','he-is-blessing','»·them'])
        self.assertEqual([u['source_spans'] for u in out['ordered_units']],
                         [[0],[3],[0,1],[2]])
        self.assertEqual(out['moves'][0]['rule'],'VOS_TO_SVO_CVOT_BOLD_OBJECT_ANCHORED')
    def test_vos_prepositional_object(self):
        out=reorder_verse(['and·he-is-saying','to·them','Elohim'],
                          ['And','Elohim','said','to','them'])
        self.assertEqual([u['text'] for u in out['ordered_units']],
                         ['and','Elohim','he-is-saying','to·them'])
    def test_nonmatching_object_remains(self):
        src=['and·he-is-blessing','»·him','Elohim']
        out=reorder_verse(src,['And','Elohim','blessed','him'])
        self.assertEqual([u['text'] for u in out['ordered_units']],src)
    def test_wrong_cvot_order_remains(self):
        src=['and·he-is-blessing','»·them','Elohim']
        out=reorder_verse(src,['And','them','Elohim','blessed'])
        self.assertEqual([u['text'] for u in out['ordered_units']],src)
    def test_lexical_mismatch_remains(self):
        src=['and·he-is-giving','»·them','Elohim']
        out=reorder_verse(src,['And','Elohim','placed','them'])
        self.assertEqual([u['text'] for u in out['ordered_units']],src)
    def test_multiple_independent_anchors(self):
        src=['and·he-is-blessing','»·them','Elohim',
             'and·he-is-saying','to·them','Elohim']
        out=reorder_verse(src,['Elohim','blessed','them','and',
                               'Elohim','said','to','them'])
        self.assertEqual(len(out['moves']),2)
        self.assertEqual([u['text'] for u in out['ordered_units']],
                         ['and','Elohim','he-is-blessing','»·them',
                          'and','Elohim','he-is-saying','to·them'])
    def test_span_and_lexeme_invariants(self):
        src=['c','and·he-is-','blessing','»·them','Elohim','(p)']
        out=reorder_verse(src,['Elohim','blessed','them'])
        ids={i for u in out['ordered_units'] for i in u['source_spans']}
        self.assertEqual(ids,set(range(len(src))))
        self.assertTrue(out['source_spans_preserved'])
        self.assertTrue(out['source_lexemes_preserved'])
    def test_crossing_clause_anchors_blocked(self):
        src=['and·he-is-saying','Elohim','and·he-is-seeing','Elohim']
        out=reorder_verse(src,['Elohim','saw','and','Elohim','said'])
        self.assertLessEqual(len(out['moves']),1)
        self.assertTrue(out['cvot_anchor_order_preserved'])
if __name__=='__main__':
    unittest.main()
