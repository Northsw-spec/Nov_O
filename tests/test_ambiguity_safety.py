"""Synthetic regression cases only; source corpora stay out of Git."""
import unittest
from nov_o.engine import reorder_verse

class AmbiguitySafetyTests(unittest.TestCase):
    def test_editorial_interruption_in_name_fails_closed(self):
        source=['he-made','Yahweh','(p)','Elohim']
        result=reorder_verse(source,['Yahweh','Elohim','made'])
        self.assertEqual(result['status'],'UNRESOLVED')
        self.assertEqual([x['text'] for x in result['ordered_units']],source)
        self.assertEqual(result['moves'],[])

    def test_adjacent_yahweh_elohim_still_moves_as_one_unit(self):
        result=reorder_verse(['and·he-is-saying','Yahweh','Elohim','to·them'],
                             ['And','Yahweh','Elohim','said','to','them'])
        self.assertEqual([x['text'] for x in result['ordered_units']],
                         ['and','Yahweh','Elohim','he-is-saying','to·them'])
        self.assertEqual(result['moves'][0]['subject_source_indices'],[[1],[2]])

    def test_duplicate_vso_bold_anchor_rejected(self):
        source=['and·he-is-creating','Elohim']
        result=reorder_verse(source,['Elohim','created','more','words','Elohim','created'])
        self.assertEqual(result['status'],'UNRESOLVED')
        self.assertEqual([x['text'] for x in result['ordered_units']],source)

    def test_duplicate_vos_bold_anchor_rejected(self):
        source=['and·he-is-blessing','»·them','Elohim']
        result=reorder_verse(source,['Elohim','blessed','them','and','Elohim','blessed','them'])
        self.assertEqual(result['status'],'UNRESOLVED')
        self.assertEqual([x['text'] for x in result['ordered_units']],source)

    def test_unique_vso_bold_anchor_accepted(self):
        result=reorder_verse(['and·he-is-creating','Elohim'],['And','Elohim','created'])
        self.assertEqual([x['text'] for x in result['ordered_units']],
                         ['and','Elohim','he-is-creating'])

    def test_lexemes_and_span_ids_are_preserved(self):
        source=['(p)','and·he-is-saying','Yahweh','Elohim','to·them']
        result=reorder_verse(source,['And','Yahweh','Elohim','said','to','them'])
        self.assertTrue(result['source_lexemes_preserved'])
        self.assertTrue(result['source_spans_preserved'])
        ids={n for item in result['ordered_units'] for n in item['source_spans']}
        self.assertEqual(ids,set(range(len(source))))

if __name__ == '__main__':
    unittest.main()
