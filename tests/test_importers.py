import unittest

from soilclass.importers.table_parser import parse_text


class TestTableParser(unittest.TestCase):
    def test_plain_pairs(self):
        d = parse_text("4.75 83\n2.00 65\n0.075 28\nLL = 38\nPL: 19")
        self.assertEqual(len(d.sieve), 3)
        self.assertEqual(d.sieve[0], (4.75, 83.0))
        self.assertEqual(d.liquid_limit, 38.0)
        self.assertEqual(d.plastic_limit, 19.0)

    def test_sieve_designations(self):
        d = parse_text('3/4" 98\nNo. 4  83\n#10 65\nNo.200 28')
        sizes = [s for s, _ in d.sieve]
        self.assertIn(19.0, sizes)
        self.assertIn(4.75, sizes)
        self.assertIn(2.0, sizes)
        self.assertIn(0.075, sizes)
        self.assertEqual(dict(d.sieve)[0.075], 28.0)

    def test_comma_decimals(self):
        d = parse_text("0,425 45,5\n0,075 28,0")
        self.assertEqual(d.sieve[0], (0.425, 45.5))

    def test_noise_lines_skipped(self):
        d = parse_text("Project 2026-113\nSample BH-1 depth 3.5\n"
                       "Date 06/07/2026\n4.75 83\n0.075 28")
        self.assertEqual(len(d.sieve), 2)

    def test_increasing_passing_warns(self):
        d = parse_text("4.75 50\n0.425 80\n0.075 20")
        self.assertTrue(any("increases" in w for w in d.warnings))

    def test_insufficient(self):
        d = parse_text("hello world")
        self.assertFalse(d.ok)


if __name__ == "__main__":
    unittest.main()
