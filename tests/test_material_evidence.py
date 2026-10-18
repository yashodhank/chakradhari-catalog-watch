"""Evidence must survive extraction and must not become an unsupported value."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import update_catalog
from metal_valuation import metal_estimate

class MaterialEvidenceTests(unittest.TestCase):
    def estimate(self, **kw):
        return metal_estimate(dict(name='Silver bowl', weightSize='10 g', **kw), {'Silver 999': 100000})

    def test_screenshot_ingredient_claims_survive_without_alloy_value(self):
        value = metal_estimate(dict(name='Ritika Brass Thali Set', material='Copper, Brass, Tin, Zinc',
            specificationEvidence='Material Composition Crafted from Ritika Brass made using 99.9% pure Nepaliya Copper and 99.9% pure Zinc. Set includes wooden spoon. Tin coating.'), {})
        self.assertEqual({c['metal']:c['purity'] for c in value['purityClaims']}, {'Copper':999,'Zinc':999})
        self.assertEqual(value['purityScope'], 'component_claims_not_finished_purity')
        self.assertEqual(value['status'], 'plated_or_coated')
        self.assertNotIn('metalValue', value)
        self.assertNotIn('purity', value)

    def test_specification_purity_reaches_calculation(self):
        self.assertEqual(self.estimate(specificationEvidence='Purity: 99.9%')['metalValue'], 1000)
        self.assertEqual(self.estimate(specificationEvidence='Silver purity: 92.5%')['purity'], 925)

    def test_conflicts_across_notations_and_fields(self):
        value = self.estimate(subtitle='925 Silver', specificationEvidence='99.9% pure Silver')
        self.assertEqual(value['status'], 'purity_conflict')
        self.assertNotIn('metalValue', value)
        value = metal_estimate(dict(name='18K Gold chain', weightSize='10g', specificationEvidence='22K Gold'), {})
        self.assertEqual(value['status'], 'purity_conflict')

    def test_unrelated_grade_number_not_purity(self):
        self.assertNotIn('purity', self.estimate(subtitle='Model 925, length 950 mm'))
        self.assertNotIn('purity', self.estimate(subtitle='Silver 925 grams'))

    def test_gross_range_and_coating_survive_flattened_weight(self):
        for evidence, status in [('Gross weight 10g; 999 Silver','net_metal_weight_unknown'),
                                 ('999 Silver coating','plated_or_coated'),
                                 ('999 Silver; weight 8–10g','weight_ambiguous'),
                                 ('999 Silver; up to 10g','weight_ambiguous')]:
            with self.subTest(evidence=evidence):
                self.assertEqual(self.estimate(specificationEvidence=evidence)['status'], status)

    def test_foreign_currency_does_not_create_inr_residual(self):
        value = self.estimate(subtitle='999 Silver', regular=10, currency='USD')
        self.assertEqual(value['metalValue'], 1000)
        self.assertNotIn('retailResidual', value)

    def test_set_weight_needs_quantity_basis(self):
        value = metal_estimate(dict(name='999 Silver coins (11 Piece) - 1set', weightSize='10g'), {'Silver 999':100000})
        self.assertEqual(value['status'], 'quantity_basis_unknown')
        value = metal_estimate(dict(name='999 Silver coins (11 Piece) - 1set', weightSize='10g', specificationEvidence='Total weight 10g'), {'Silver 999':100000})
        self.assertEqual(value['metalValue'], 1000)

    def test_free_shipping_is_not_shipping_weight(self):
        self.assertEqual(self.estimate(subtitle='999 Silver, free shipping')['status'], 'estimated')

    def test_thousands_and_fractional_weights_are_not_truncated(self):
        for raw, grams in [('1,200 g',1200),('.5 g',0.5)]:
            value = metal_estimate(dict(name='999 Silver',weightSize=raw), {'Silver 999':100000})
            self.assertEqual(value['weightGrams'],grams)

    def test_scraper_does_not_truncate_weight(self):
        product = {'product_name':'999 Silver bowl', 'weight':'1,200 g','variants':[]}
        html = '<script>Theme.ProductData = '+json.dumps({'product':product})+'; Theme.Utils.Product.initProduct</script>'
        with patch.object(update_catalog,'fetch',return_value=(200,html.encode(),'text/html')):
            _,status,row,error = update_catalog.product_page('https://www.chakradhari.com/products/test')
        self.assertEqual(status,'success',error)
        self.assertEqual(row['weight_size_observed'],'1,200 g')

    def test_structured_purity_label_is_retained(self):
        evidence = update_catalog.merchant_evidence({'purity':'99.9%', 'net_weight':{'value':10,'unitText':'g'}})
        self.assertIn('purity: 99.9%', evidence)
        self.assertIn('net weight: 10 g', evidence)
        self.assertEqual(self.estimate(specificationEvidence=evidence)['purity'], 999)

    def test_table_does_not_discard_third_column(self):
        evidence = update_catalog.visible_specification_evidence('<table><tr><td>Weight</td><td>10g</td><td>20g</td></tr></table>')
        self.assertIn('10g 20g', evidence)

    def test_parenthetical_quantity_is_evidence_not_missing(self):
        for name, evidence in [('999 Silver Toe Ring Pair','Weight Approx. 11 grams (pair)'),
                               ('999 Silver Water Purifier 7 Piece (1 Set)','Weight Approx. 11 grams (7 pieces)')]:
            value=metal_estimate(dict(name=name, weightSize='11 grams', specificationEvidence=evidence), {'Silver 999':100000})
            self.assertEqual(value['status'],'estimated')
        value=metal_estimate(dict(name='999 Silver 7 Piece Set', weightSize='11 grams', specificationEvidence='11 grams (5 pieces)'), {'Silver 999':100000})
        self.assertEqual(value['status'],'quantity_basis_unknown')

    def test_scraper_retains_table_labels_and_purity(self):
        product = {'product_name':'Silver bowl','variants':[]}
        html = '<script>Theme.ProductData = '+json.dumps({'product':product})+'; Theme.Utils.Product.initProduct</script>'
        html += '<table><tr><td>Purity</td><td>99.9% Silver</td></tr><tr><td>Gross weight</td><td>10 g</td></tr></table>'
        with patch.object(update_catalog,'fetch',return_value=(200,html.encode(),'text/html')):
            _,status,row,error = update_catalog.product_page('https://www.chakradhari.com/products/test')
        self.assertEqual(status,'success',error)
        self.assertIn('Purity 99.9% Silver',row['specification_evidence_observed'])
        self.assertIn('Gross weight 10 g',row['specification_evidence_observed'])
        self.assertEqual(row['weight_size_observed'],'10 g')
