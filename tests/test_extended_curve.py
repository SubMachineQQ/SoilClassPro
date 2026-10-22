import unittest

from soilclass.models import SoilSample


class TestExtendedCurve(unittest.TestCase):
    def _sample(self):
        return SoilSample(sieve_data=[
            (0.1, 31.0), (1.18, 54.0), (3.0, 45.0), (4.5, 38.0),
        ])

    def test_interior_matches_percent_passing(self):
        s = self._sample()
        xs = [2.0, 0.5]
        ext = s.extended_curve(xs)
        for x, y in zip(xs, ext):
            self.assertAlmostEqual(y, s.percent_passing(x), places=6)

    def test_extrapolates_beyond_coarse_end_instead_of_clamping_flat(self):
        s = self._sample()
        d_max = s.sieve_data[-1][0]
        clamped = s.percent_passing(d_max * 5)
        extrapolated = s.extended_curve([d_max * 5])[0]
        self.assertNotAlmostEqual(clamped, extrapolated, places=3)

    def test_extrapolates_beyond_fine_end_instead_of_clamping_flat(self):
        s = self._sample()
        d_min = s.sieve_data[0][0]
        clamped = s.percent_passing(d_min / 5)
        extrapolated = s.extended_curve([d_min / 5])[0]
        self.assertNotAlmostEqual(clamped, extrapolated, places=3)

    def test_extrapolation_is_clipped_to_0_100(self):
        s = SoilSample(sieve_data=[(10.0, 90.0), (20.0, 99.0)])
        y = s.extended_curve([500.0])[0]
        self.assertLessEqual(y, 100.0)
        self.assertGreaterEqual(y, 0.0)

        s2 = SoilSample(sieve_data=[(0.01, 5.0), (0.02, 10.0)])
        y2 = s2.extended_curve([0.0001])[0]
        self.assertGreaterEqual(y2, 0.0)
        self.assertLessEqual(y2, 100.0)

    def test_empty_sample_returns_none_list(self):
        s = SoilSample(sieve_data=[])
        result = s.extended_curve([1.0, 2.0, 3.0])
        self.assertEqual(result, [None, None, None])

    def test_single_point_sample_returns_none_like_empty(self):
        s = SoilSample(sieve_data=[(1.0, 50.0)])
        result = s.extended_curve([10.0, 1.0, 0.1])
        self.assertEqual(result, [None, None, None])


if __name__ == "__main__":
    unittest.main()
