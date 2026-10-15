import unittest
from main import Investigation

class GameTests(unittest.TestCase):
    def setUp(self):
        self.case = Investigation()

    def test_search(self):
        self.assertEqual(self.case.binary_search(107).title, 'Admin Audit Trail')
        self.assertIsNone(self.case.binary_search(999))
        self.assertEqual(len(self.case.linear_search('token')), 2)

    def test_sort(self):
        result = self.case.bubble_sort_by_time()
        self.assertEqual([e.timestamp for e in result], sorted(e.timestamp for e in result))

    def test_stack(self):
        self.case.discover(103)
        self.case.discover(107)
        self.assertEqual(self.case.undo().code, 107)
        self.assertEqual(self.case.detective.discovered, {103})

    def test_queue(self):
        for code in (107, 103):
            self.case.discover(code)
            self.case.enqueue(code)
        self.assertEqual(self.case.process_next().code, 107)
        self.assertEqual(self.case.process_next().code, 103)
        self.assertIsNone(self.case.process_next())

    def test_duplicate(self):
        self.assertTrue(self.case.discover(103))
        self.assertFalse(self.case.discover(103))
        self.assertTrue(self.case.enqueue(103))
        self.assertFalse(self.case.enqueue(103))

if __name__ == '__main__':
    unittest.main()
