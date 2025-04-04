import unittest
from time_interval import is_data_available, add_one_day, subtract_one_day


class TestTimeIntervals(unittest.TestCase):
    def setUp(self):
        # Common date strings for reuse in tests
        self.jan_01 = "01-01-2025"
        self.jan_10 = "10-01-2025"
        self.jan_15 = "15-01-2025"
        self.jan_20 = "20-01-2025"
        self.feb_15 = "15-02-2025"
        self.mar_31 = "31-03-2025"
        self.apr_01 = "01-04-2025"
        self.apr_30 = "30-04-2025"

    def test_complete_overlap(self):
        """Test when the interval completely overlaps the requested period."""
        intervals = [[self.jan_01, self.mar_31]]
        result = is_data_available(intervals, self.jan_10, self.jan_20)

        self.assertIsNone(result['need'])
        self.assertEqual(result['start'], [self.jan_10, self.mar_31])
        self.assertEqual(result['end'], [self.jan_01, self.jan_20])

    def test_no_overlap(self):
        """Test when there is no overlap between intervals and requested period."""
        intervals = [[self.apr_01, self.apr_30]]
        result = is_data_available(intervals, self.jan_10, self.jan_20)

        self.assertEqual(result['need'], [self.jan_10, self.jan_20])
        self.assertIsNone(result['start'])
        self.assertIsNone(result['end'])

    def test_partial_overlap_start(self):
        """Test when interval overlaps with the end of the requested period."""
        intervals = [[self.jan_15, self.mar_31]]
        result = is_data_available(intervals, self.jan_10, self.jan_20)

        self.assertEqual(result['need'], [self.jan_10, "14-01-2025"])
        self.assertEqual(result['start'], [self.jan_10, self.mar_31])
        self.assertEqual(result['end'], [self.jan_15, self.jan_20])

    def test_partial_overlap_end(self):
        """Test when interval overlaps with the beginning of the requested period."""
        intervals = [[self.jan_01, self.jan_15]]
        result = is_data_available(intervals, self.jan_10, self.jan_20)

        self.assertEqual(result['need'], ["16-01-2025", self.jan_20])
        self.assertEqual(result['start'], [self.jan_10, self.jan_15])
        self.assertIsNone(result['end'])

    def test_gap_in_middle(self):
        """Test when there's a gap between two intervals in the requested period."""
        intervals = [[self.jan_01, self.jan_10], [self.jan_15, self.mar_31]]
        result = is_data_available(intervals, "05-01-2025", self.jan_20)

        self.assertEqual(result['need'], ["11-01-2025", "14-01-2025"])
        self.assertEqual(result['start'], ["05-01-2025", self.jan_10])
        self.assertEqual(result['end'], [self.jan_15, self.jan_20])

    def test_empty_intervals(self):
        """Test when no intervals are provided."""
        intervals = []
        result = is_data_available(intervals, self.jan_10, self.jan_20)

        self.assertEqual(result['need'], [self.jan_10, self.jan_20])
        self.assertIsNone(result['start'])
        self.assertIsNone(result['end'])

    def test_multiple_overlapping_intervals(self):
        """Test with multiple overlapping intervals that need to be merged."""
        intervals = [
            [self.jan_01, self.jan_15],
            [self.jan_10, self.feb_15],
            [self.feb_15, self.mar_31]
        ]
        result = is_data_available(intervals, self.jan_10, self.jan_20)

        self.assertIsNone(result['need'])
        self.assertEqual(result['start'], [self.jan_10, self.mar_31])
        self.assertEqual(result['end'], [self.jan_01, self.jan_20])

    def test_adjacent_intervals(self):
        """Test with adjacent intervals that should be merged."""
        # Create adjacent dates
        jan_11 = "11-01-2025"
        jan_12 = "12-01-2025"

        intervals = [
            [self.jan_01, self.jan_10],
            [jan_11, self.jan_20]
        ]
        result = is_data_available(intervals, "05-01-2025", self.jan_15)

        self.assertIsNone(result['need'])
        self.assertEqual(result['start'], ["05-01-2025", self.jan_20])
        self.assertEqual(result['end'], [self.jan_01, self.jan_15])

    def test_edge_case_one_day(self):
        """Test when requested period is just one day."""
        intervals = [[self.jan_01, self.mar_31]]
        result = is_data_available(intervals, self.jan_10, self.jan_10)

        self.assertIsNone(result['need'])
        self.assertEqual(result['start'], [self.jan_10, self.mar_31])
        self.assertEqual(result['end'], [self.jan_01, self.jan_10])

    def test_helper_functions(self):
        """Test the helper functions add_one_day and subtract_one_day."""
        self.assertEqual(add_one_day("10-01-2025"), "11-01-2025")
        self.assertEqual(subtract_one_day("10-01-2025"), "09-01-2025")

        # Test month boundary
        self.assertEqual(add_one_day("31-01-2025"), "01-02-2025")
        self.assertEqual(subtract_one_day("01-01-2025"), "31-12-2024")

        # Test year boundary
        self.assertEqual(add_one_day("31-12-2024"), "01-01-2025")
        self.assertEqual(subtract_one_day("01-01-2025"), "31-12-2024")


if __name__ == "__main__":
    unittest.main()
