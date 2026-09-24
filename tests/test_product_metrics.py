import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from product_metrics import product_asking_per_carat

class UnitPriceTests(unittest.TestCase):
    def test_single_carat_is_listing_total_not_gemstone_valuation(self):
        metric = product_asking_per_carat('Diamond with silver ring', 'Diamond', '0.31 Carat', 31000)
        self.assertEqual(metric['amount'], 100000)
        self.assertIn('may include a setting', metric['basis'])

    def test_range_or_quote_price_is_not_divided_by_one_endpoint(self):
        self.assertIsNone(product_asking_per_carat('02.30 To 02.80 Carats Rose Quartz', 'Quartz', '2.80 Carats', 4000))
        self.assertIsNone(product_asking_per_carat('Diamond', 'Diamond', '0.31 Carat', None))

if __name__ == '__main__':
    unittest.main()
