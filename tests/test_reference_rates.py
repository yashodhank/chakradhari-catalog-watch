import io
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from update_reference_rates import fx_reference, monthly_prices

class RateParserTests(unittest.TestCase):
    def test_monthly_workbook_and_ecb_cross_rate(self):
        xml = '''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
        <row><c r="A1" t="inlineStr"><is><t>Date</t></is></c>
        <c r="B1" t="inlineStr"><is><t>Aluminum</t></is></c>
        <c r="C1" t="inlineStr"><is><t>Copper</t></is></c>
        <c r="D1" t="inlineStr"><is><t>Tin</t></is></c></row>
        <row><c r="A2" t="inlineStr"><is><t>2026M08</t></is></c>
        <c r="B2"><v>2600</v></c><c r="C2"><v>10000</v></c><c r="D2"><v>33000</v></c></row>
        </sheetData></worksheet>'''
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as z:
            z.writestr('xl/worksheets/sheet1.xml', xml)
        month, values = monthly_prices(buffer.getvalue())
        self.assertEqual(month, '2026-08')
        self.assertEqual(values['Aluminium'], 2600)
        self.assertEqual(values['Copper'], 10000)
        date, conversion = fx_reference(b'<Envelope><Cube time="2026-09-24"><Cube currency="USD" rate="1.1"/><Cube currency="INR" rate="99"/></Cube></Envelope>')
        self.assertEqual(date, '2026-09-24')
        self.assertAlmostEqual(conversion, 90)

if __name__ == '__main__':
    unittest.main()
