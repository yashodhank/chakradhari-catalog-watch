"""Regression for a visible quote-only product with stale structured data."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import update_catalog


class ProductExtractionTests(unittest.TestCase):
    def test_visible_contact_price_overrides_stale_schema_price(self):
        url = 'https://www.chakradhari.com/products/example'
        product = {
            'id': '1004004', 'product_name': 'Diamond with Silver Ring',
            'hide_price': '1', 'available': True,
            'featured_image_url': 'https://cdn.shopaccino.com/chakradhari/products/current_m.jpg',
            'variants': [
                {'id': '1', 'size': 'Male', 'thumb_image': 'https://cdn.shopaccino.com/chakradhari/products/current_s.jpg',
                 'product_price': 0, 'compare_at_price': 0, 'allow_purchase': '0', 'show_as_main': 1},
                {'id': '2', 'size': 'Female', 'product_price': 0},
            ],
        }
        schema = {'@type': 'Product', 'name': 'Diamond with Silver Ring',
                  'image': ['https://cdn.shopaccino.com/chakradhari/products/old_s.jpg'],
                  'offers': {'price': '45900', 'priceCurrency': 'INR'}}
        html = ('<script>Theme.ProductData = '+json.dumps({'product': product})+'; '
                'Theme.Utils.Product.initProduct</script>'
                '<script type="application/ld+json">'+json.dumps(schema)+'</script>'
                '<a>Contact us for price</a>')
        with patch.object(update_catalog, 'fetch', return_value=(200,html.encode(),'text/html')):
            _, status, row, error = update_catalog.product_page(url)
        self.assertEqual(status,'success',error)
        self.assertEqual(row['gender_observed'],'Unisex')
        self.assertEqual(row['price_status_observed'],'contact_for_price')
        self.assertEqual(row['regular_price_normalized'],'')
        self.assertEqual(row['availability_normalized'],'unknown')
        self.assertIn('current_s.jpg',row['primary_image_url'])
        self.assertEqual(len(json.loads(row['image_candidates_observed'])),3)

    def test_localized_usd_price_is_not_labeled_as_rupees(self):
        url = 'https://www.chakradhari.com/products/example-usd'
        product = {
            'id': '2001', 'product_name': 'Localized Product',
            'hide_price': '0', 'available': True,
            'variants': [{'id': '2', 'sku': 'USD-2', 'product_price': 840,
                          'compare_at_price': 0, 'allow_purchase': '1', 'show_as_main': 1}],
        }
        schema = {'@type': 'Product', 'name': 'Stale Schema Name',
                  'offers': {'price': '8.40', 'priceCurrency': 'USD',
                             'availability': 'https://schema.org/InStock'}}
        html = ('<script>Theme.ProductData = '+json.dumps({'product': product})+'; '
                'Theme.Utils.Product.initProduct</script>'
                '<script type="application/ld+json">'+json.dumps(schema)+'</script>')
        with patch.object(update_catalog, 'fetch', return_value=(200,html.encode(),'text/html')):
            _, status, row, error = update_catalog.product_page(url)
        self.assertEqual(status,'success',error)
        self.assertEqual(row['name_observed'],'Localized Product')
        self.assertEqual(row['currency_normalized'],'USD')
        self.assertEqual(row['regular_price_observed'],'US $ 8.40')
        self.assertEqual(row['regular_price_normalized'],8.4)

    def test_json_ld_price_wins_when_product_data_is_edge_localized(self):
        url = 'https://www.chakradhari.com/products/example-localized'
        product = {
            'id': '3001', 'product_name': 'Emerald',
            'hide_price': '0', 'available': True,
            'variants': [{'id': '3', 'product_price': 54374,
                          'compare_at_price': 0, 'allow_purchase': '1', 'show_as_main': 1}],
        }
        schema = {'@type': 'Product', 'name': 'Emerald',
                  'offers': {'price': '38838.40', 'priceCurrency': 'INR',
                             'availability': 'https://schema.org/InStock'}}
        html = ('<script>Theme.ProductData = '+json.dumps({'product': product})+'; '
                'Theme.Utils.Product.initProduct</script>'
                '<script type="application/ld+json">'+json.dumps(schema)+'</script>')
        with patch.object(update_catalog, 'fetch', return_value=(200,html.encode(),'text/html')):
            _, status, row, error = update_catalog.product_page(url)
        self.assertEqual(status,'success',error)
        self.assertEqual(row['currency_normalized'],'INR')
        self.assertEqual(row['regular_price_observed'],'₹ 38,838.40')
        self.assertEqual(row['regular_price_normalized'],38838.4)


if __name__ == '__main__':
    unittest.main()
