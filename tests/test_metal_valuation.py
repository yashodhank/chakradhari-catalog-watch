import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from metal_valuation import metal_estimate


class MetalValuationTests(unittest.TestCase):
    def estimate(self, name, **kw):
        return metal_estimate(dict(name=name, regular=1000, **kw), {'Silver 999': 100000, 'Gold 999': 70000})

    def test_word_boundary(self):
        self.assertIsNone(self.estimate('Golden marigold flower'))

    def test_plating_not_solid(self):
        self.assertEqual(self.estimate('999 silver plated copper bowl 10 g')['status'], 'plated_or_coated')

    def test_variants_not_minimum(self):
        self.assertEqual(self.estimate('999 Silver coin 10 g / 20 g')['status'], 'weight_ambiguous')
        self.assertEqual(self.estimate('999 Silver coin 10-20 g')['status'], 'weight_ambiguous')

    def test_no_blanket_purity(self):
        self.assertEqual(self.estimate('Pure copper bowl 100 g')['status'], 'purity_unknown')

    def test_no_blanket_tax(self):
        value = self.estimate('999 Silver coin 10 g')
        self.assertEqual(value['metalValue'], 1000)
        self.assertNotIn('estimatedGstIncluded', value)
        self.assertEqual(value['retailResidual'], 0)

    def test_alloy_no_recipe(self):
        for name in ['Brass', 'Bronze', 'Kansa', 'Panchdhatu', 'Stainless steel']:
            self.assertEqual(self.estimate(name + ' bowl 100 g')['status'], 'composition_unknown')

    def test_other_metals_supported(self):
        for name in ['Copper', 'Tin', 'Ranga', 'Zinc', 'Aluminium', 'Lead', 'Nickel', 'Iron', 'Mercury', 'Parad']:
            self.assertIsNotNone(self.estimate(name + ' 100 g'))

    def test_validated_copper_rate(self):
        value = metal_estimate({'name': '99.9% Copper bowl 100 g', 'regular': 200}, {}, rate_metadata={
            'Copper': {'ratePerGram': 1, 'currency': 'INR', 'purity': 1000, 'source': 'manual user input', 'date': '2026-09-22', 'basis': 'manual_scenario'}})
        self.assertEqual(value['metalValue'], 99.9)
        self.assertEqual(value['rateBasis'], 'manual_scenario')

    def test_unknown_currency_rejected(self):
        value = metal_estimate({'name': '99.9% Copper bowl 100 g'}, {}, rate_metadata={'Copper': {'ratePerGram': 1, 'currency': 'USD'}})
        self.assertEqual(value['status'], 'rate_missing')

    def test_gross_and_composite(self):
        self.assertEqual(self.estimate('999 Silver coin gross weight 10 g')['status'], 'net_metal_weight_unknown')
        self.assertEqual(self.estimate('999 Silver rudraksha bracelet 10 g')['status'], 'net_metal_weight_unknown')

    def test_weight_not_purity(self):
        self.assertEqual(self.estimate('Silver bowl 925 g')['status'], 'purity_unknown')

    def test_weight_size_preferred(self):
        self.assertEqual(self.estimate('999 Silver coin 10 g / 20 g', weightSize='10 g')['weightGrams'], 10)


if __name__ == '__main__':
    unittest.main()
