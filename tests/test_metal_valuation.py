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

    def test_mixed_material_explains_why_raw_metal_comparison_is_blocked(self):
        value = self.estimate('Copper and brass ring')
        self.assertEqual(value['status'], 'composition_unknown')
        self.assertEqual(value['calculationState'], 'unavailable')
        self.assertEqual(value['missingEvidence'], ['alloy composition', 'net metal weight'])

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

    def test_standard_karat_claims_use_the_published_benchmark_grade(self):
        value = self.estimate('22K Gold chain 11 g')
        self.assertEqual(value['purity'], 916)

    def test_screenshot_variants_preserve_purity_without_price_guess(self):
        result = self.estimate('99.6% Silver Kacchi Kairi Payal',
                               weightSize='9 Inch; 43gm; 10 Inch; 47gm; 11 Inch; 52gm')
        self.assertEqual(result['status'], 'variant_estimates')
        self.assertEqual(result['purity'], 996)
        self.assertEqual([v['weightGrams'] for v in result['variants']], [43, 47, 52])
        self.assertAlmostEqual(result['variants'][0]['fineMetalGrams'], 42.828)
        self.assertEqual(result['variants'][0]['metalValue'], round(43 * 100 * 996 / 999, 2))
        for value in [result] + result['variants']:
            self.assertNotIn('retailResidual', value)
            self.assertNotIn('listedPrice', value)

    def test_missing_weight_keeps_known_purity(self):
        result = self.estimate('99.6% Silver Payal')
        self.assertEqual(result['status'], 'weight_missing')
        self.assertEqual(result['purity'], 996)

    def test_incomplete_or_reordered_pairs_stay_blocked(self):
        for weights in ['11 Inch; 9 Inch; 106gm; 10 Inch; 115gm; 127gm',
                        '190ml; 156g; 47g', '9 Inch; 43gm; 10 Inch; 47gm; 52gm']:
            self.assertEqual(self.estimate('99.6% Silver item', weightSize=weights)['status'], 'weight_ambiguous')

    def test_conflicting_purity_blocked(self):
        self.assertEqual(self.estimate('99.6% Silver Payal', subtitle='99.9% Silver', weightSize='43g')['status'], 'purity_conflict')

    def test_variant_safeguards(self):
        for name in ['999 Silver plated payal', '999 Silver rudraksha payal', 'Silver payal']:
            result = self.estimate(name, weightSize='9 Inch; 43gm; 10 Inch; 47gm')
            self.assertNotEqual(result['status'], 'variant_estimates')

    def test_benchmark_provenance_and_kg(self):
        result = metal_estimate({'name': '99.9% Silver bar', 'weightSize': '1kg'},
                                {'Silver 999': 100000}, benchmark_metadata={'date': '2026-10-16', 'source': 'test'})
        self.assertEqual(result['metalValue'], 100000)
        self.assertEqual(result['fineMetalGrams'], 999)
        self.assertEqual(result['rateDate'], '2026-10-16')


if __name__ == '__main__':
    unittest.main()
