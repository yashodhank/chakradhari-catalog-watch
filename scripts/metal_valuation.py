"""Conservative retail metal estimates. Missing evidence stays missing.

Additional rate records use {metal: {ratePerGram, currency: 'INR',
source, date, purity: 1000, basis: 'benchmark'|'manual_scenario'}}.
No alloy recipe, retail tax rate, or unspecified purity is invented.
"""
import math
import re

ALIASES = {
    'Gold': r'gold|sona|स्वर्ण|सोना',
    'Silver': r'silver|chandi|चांदी|रजत',
    'Platinum': r'platinum',
    'Copper': r'copper|tamba|tamra|तांबा|ताम्र',
    'Tin': r'tin|ranga|रांगा',
    'Zinc': r'zinc|jasta|जस्ता',
    'Aluminium': r'aluminium|aluminum',
    'Lead': r'lead|सीसा',
    'Nickel': r'nickel',
    'Iron': r'iron|loha|लोहा',
    'Steel': r'steel|stainless',
    'Brass': r'brass|pital|peetal|पीतल',
    'Bronze': r'bronze|kansa|kansya|कांसा|कांस्य',
    'Panchdhatu': r'panch[ -]?(?:dhatu|dhaatu|dhathu)|पंचधातु',
    'Mercury': r'mercury|parad|पारद',
}
ALLOYS = {'Steel', 'Brass', 'Bronze', 'Panchdhatu'}
WEIGHT = r'(?<![\d.])(\d+(?:\.\d+)?)\s*(kg|kilograms?|grams?|gms?|gm|g)\b'


def number(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def unavailable(result, status, *missing):
    """Keep an unavailable comparison actionable without inventing a value."""
    result.update(status=status, calculationState='unavailable', missingEvidence=list(missing))
    return result


def metal_estimate(p, rates, *, rate_metadata=None):
    """Return an evidence-labelled estimate or explicit non-estimable status."""
    fields = {k: str(p.get(k) or '') for k in ('name', 'material', 'weightSize', 'subtitle')}
    text = ' '.join(fields.values())
    # Material is the best field, but plating/composite warnings inspect all text.
    identity = fields['material'] + ' ' + fields['name']
    metals = [name for name, pattern in ALIASES.items()
              if re.search(r'(?<!\w)(?:' + pattern + r')(?!\w)', identity, re.I)]
    if not metals:
        return None
    plated = bool(re.search(r'\b(?:plat(?:ed|ing)|coated|gold[ -]filled|vermeil|silver[ -]tone|gold[ -]tone)\b', text, re.I))
    metal = metals[0] if len(metals) == 1 else ' / '.join(metals)
    result = {'metal': metal, 'detectedMetals': metals, 'materialKind': 'alloy' if any(m in ALLOYS for m in metals) else 'metal',
              'purityBasis': 'unknown', 'status': 'weight_missing', 'calculationState': 'unavailable',
              'missingEvidence': ['net metal weight'], 'taxBasis': 'unknown',
              'evidence': {k: v for k, v in fields.items() if v},
              'caveat': 'Seller claims are not independently assayed. Retail residual is not a making-charge quote.'}
    if 'Mercury' in metals:
        result['safetyNote'] = 'Parad is a seller material claim; mercury content and binding composition are unverified. No handling-safety inference.'
    if plated:
        result.update(materialKind='plated')
        return unavailable(result, 'plated_or_coated', 'solid-metal composition', 'net metal weight')
    if len(metals) > 1:
        result.update(materialKind='mixed')
        return unavailable(result, 'composition_unknown', 'alloy composition', 'net metal weight')
    # Do not silently choose the minimum of variant, gross and shipping weights.
    weight_text = fields['weightSize'] or text
    matches = list(re.finditer(WEIGHT, weight_text, re.I))
    weights = {round(float(m[1]) * (1000 if m[2].lower().startswith('k') else 1), 6) for m in matches}
    ranged = bool(re.search(r'\d\s*(?:[-–—/]|to|±)\s*\d', weight_text))
    gross = bool(re.search(r'\b(?:shipping|packed|package|gross)\s*(?:weight)?\b', weight_text, re.I))
    if ranged or len(weights) > 1:
        return unavailable(result, 'weight_ambiguous', 'one stated net metal weight')
    if not weights or not 0 < next(iter(weights)) <= 100000:
        return result
    weight = next(iter(weights))
    result.update(weightGrams=weight, weightBasis='seller_claim', weightEvidence=matches[0][0])
    if gross or re.search(r'\b(?:stone|stones|wood|wooden|rudraksha|beads|gemstone|crystal|filled)\b', text, re.I):
        return unavailable(result, 'net_metal_weight_unknown', 'net metal weight excluding non-metal parts')
    if metal in ALLOYS:
        return unavailable(result, 'composition_unknown', 'alloy composition')
    purity = None
    pct = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:pure\s*)?(?:' + ALIASES[metal] + r')\b', text, re.I)
    if not pct:
        pct = re.search(r'\b(?:purity|pure)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*%', text, re.I)
    if pct and 0 < float(pct[1]) <= 100:
        purity = float(pct[1]) * 10
    if purity is None and metal in {'Gold', 'Silver', 'Platinum'}:
        mark = re.search(r'(?<![\d.])(999(?:\.9)?|995|950|925|916|900|750|585)(?![\d.]|\s*(?:g|gm|grams?|kg)\b)', text, re.I)
        if mark:
            purity = float(mark[1])
    if purity is None and metal == 'Gold':
        karat = re.search(r'(?<!\d)(24|22|18|14)\s*(?:k|kt|karat|carat)\b', text, re.I)
        if karat:
            purity = float(karat[1]) / 24 * 1000
    if purity is None:
        return unavailable(result, 'purity_unknown', 'stated metal purity')
    result.update(purity=round(purity, 3), purityBasis='seller_claim')
    record = (rate_metadata or {}).get(metal)
    per_gram = None
    if record:
        reference = number(record.get('ratePerGram'))
        fineness = number(record.get('purity'))
        if (record.get('currency') == 'INR' and reference and reference > 0 and fineness and 0 < fineness <= 1000
                and record.get('source') and record.get('date') and record.get('basis') in {'benchmark', 'monthly_reference', 'manual_scenario'}):
            per_gram = reference * purity / fineness
            result.update(rateSource=record['source'], rateDate=record['date'], rateBasis=record['basis'])
    if per_gram is None and metal in {'Gold', 'Silver', 'Platinum'}:
        divisor = 1000 if metal == 'Silver' else 10
        exact = number(rates.get(f'{metal} {purity:g}'))
        pure = number(rates.get(f'{metal} 999'))
        if exact and exact > 0:
            per_gram = exact / divisor
        elif pure and pure > 0:
            per_gram = pure / divisor * purity / 999
        if per_gram is not None:
            result['rateBasis'] = 'benchmark'
    if per_gram is None:
        return unavailable(result, 'rate_missing', 'validated reference rate')
    value = weight * per_gram
    result.update(status='estimated', calculationState='available', missingEvidence=[], ratePerGram=round(per_gram, 4), metalValue=round(value, 2), currency='INR')
    listed = number(p.get('sale') if p.get('sale') is not None else p.get('regular'))
    if listed is not None and listed >= 0:
        result.update(listedPrice=listed, retailResidual=round(listed-value, 2),
                      metalSharePct=round(100*value/listed, 1) if listed else None)
        # Tax decomposition only from explicit product-specific evidence.
        tax = number(p.get('taxRatePct'))
        if p.get('taxIncluded') is True and tax is not None and 0 <= tax <= 100 and p.get('taxSource'):
            pretax = listed/(1+tax/100)
            result.update(estimatedGstIncluded=round(listed-pretax, 2), nonMetalPremiumPreTax=round(pretax-value, 2), taxBasis='product_evidence')
    return result
