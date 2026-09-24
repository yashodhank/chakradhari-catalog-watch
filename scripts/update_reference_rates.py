#!/usr/bin/env python3
"""Monthly World Bank raw-metal references converted with a dated ECB FX fix.

These are international commodity reference values, never daily Indian retail
quotes, alloy prices, jewellery appraisals or gemstone valuations.
"""
import io
import json
import re
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'metal-rates.json'
WORLD_BANK = 'https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx'
ECB = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
N = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
METALS = {
    'Aluminium': r'^alumin(?:um|ium)\b',
    'Copper': r'^copper\b',
    'Lead': r'^lead\b',
    'Tin': r'^tin\b',
    'Zinc': r'^zinc\b',
    'Nickel': r'^nickel\b',
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'ChakradhariCatalogMonitor/1.0'})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = response.read(12_000_001)
    if len(data) > 12_000_000:
        raise ValueError('Source too large')
    return data

def monthly_prices(data):
    """Parse the published monthly XLSX using the Python standard library."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings = [''.join(t.text or '' for t in si.findall('.//x:t', N))
                       for si in root.findall('x:si', N)]
        sheets = [n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', n)]
        if not sheets:
            raise ValueError('World Bank workbook has no worksheets')
        observations = []
        for sheet in sheets:
            root = ET.fromstring(z.read(sheet))
            rows = []
            for row in root.findall('.//x:sheetData/x:row', N):
                cells = {}
                for cell in row.findall('x:c', N):
                    col = re.match(r'[A-Z]+', cell.attrib.get('r', ''))
                    if not col:
                        continue
                    v = cell.find('x:v', N)
                    value = v.text if v is not None else ''
                    if cell.attrib.get('t') == 's' and value:
                        value = strings[int(value)]
                    elif cell.attrib.get('t') == 'inlineStr':
                        value = ''.join(t.text or '' for t in cell.findall('.//x:t', N))
                    cells[col.group()] = value
                rows.append(cells)
            for i, header in enumerate(rows[:20]):
                cols = {metal: col for col, val in header.items() for metal, pattern in METALS.items()
                        if re.search(pattern, str(val).strip(), re.I)}
                if len(cols) < 3:
                    continue
                for row in rows[i + 1:]:
                    label = str(row.get('A', '')).strip()
                    match = re.search(r'(20\d{2})\s*[-/M]\s*(0?[1-9]|1[0-2])\b', label, re.I)
                    if not match:
                        continue
                    month = f'{match[1]}-{int(match[2]):02d}'
                    prices = {}
                    for metal, col in cols.items():
                        try:
                            amount = float(str(row.get(col, '')).replace(',', ''))
                        except (TypeError, ValueError):
                            continue
                        if 100 <= amount <= 150000:
                            prices[metal] = amount
                    if prices:
                        observations.append((month, prices))
        if not observations:
            raise ValueError('No dated monthly metal values found in World Bank workbook')
        return max(observations, key=lambda pair: pair[0])

def fx_reference(data):
    root = ET.fromstring(data)
    for node in root.iter():
        if 'time' not in node.attrib:
            continue
        values = {child.attrib.get('currency'): child.attrib.get('rate') for child in node}
        if values.get('USD') and values.get('INR'):
            usd, inr = float(values['USD']), float(values['INR'])
            if 0.5 < usd < 3 and 30 < inr / usd < 200:
                return node.attrib['time'], inr / usd
    raise ValueError('ECB USD and INR reference rates unavailable')

def refresh(world_bank_data=None, ecb_data=None, now=None):
    month, values = monthly_prices(world_bank_data if world_bank_data is not None else fetch(WORLD_BANK))
    fx_date, inr_per_usd = fx_reference(ecb_data if ecb_data is not None else fetch(ECB))
    now = now or datetime.now(timezone.utc)
    if datetime.fromisoformat(month + '-01').date() < (now.date().replace(day=1) - timedelta(days=75)):
        raise ValueError('World Bank observation is stale')
    if datetime.fromisoformat(fx_date).date() < now.date() - timedelta(days=8):
        raise ValueError('ECB reference is stale')
    rates = {metal: {'ratePerGram': round(usd_per_tonne * inr_per_usd / 1_000_000, 5),
                     'currency': 'INR', 'purity': 1000, 'basis': 'monthly_reference',
                     'date': month, 'source': WORLD_BANK, 'fxSource': ECB, 'fxDate': fx_date,
                     'unit': 'INR per gram', 'context': 'International bulk commodity average, not Indian retail'}
             for metal, usd_per_tonne in values.items()}
    existing = json.loads(OUT.read_text('utf-8'))
    latest = existing.get('latest', {})
    latest['otherRates'] = rates
    latest['monthlyReference'] = {'month': month, 'fxDate': fx_date, 'fxInrPerUsd': round(inr_per_usd, 6),
                                  'worldBankSource': WORLD_BANK, 'fxSource': ECB, 'observedAt': now.isoformat()}
    history = existing.setdefault('referenceHistory', [])
    if not any(x.get('month') == month and x.get('fxDate') == fx_date for x in history):
        history.append(dict(latest['monthlyReference'], rates=rates))
    existing['latest'] = latest
    OUT.write_text(json.dumps(existing, ensure_ascii=False, indent=2), 'utf-8')
    return latest['monthlyReference']

if __name__ == '__main__':
    try:
        print(json.dumps(refresh()))
    except Exception as error:
        # A failed supplementary feed must not erase the verified IBJA data.
        print(f'Monthly reference unavailable; retaining last valid rates: {error}')
