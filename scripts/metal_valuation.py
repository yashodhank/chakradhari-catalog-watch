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
WEIGHT = r'(?<![\d.,])((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)\s*(kg|kilograms?|grams?|gms?|gm|g)\b'


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



def purity_claims(text, metals):
    """Keep metal-scoped source wording; ingredient purity is not an alloy ratio."""
    claims = []
    for metal in metals:
        alias = '(?:' + ALIASES[metal] + ')'
        patterns = [
            (r'(?<![\d.])(\d+(?:\.\d+)?)\s*%\s*(?:pure\s+)?(?:Nepaliya\s+)?' + alias + r'(?!\w)', 10),
            (r'(?<!\w)' + alias + r'\s*(?:purity\s*)?[:=-]?\s*(\d+(?:\.\d+)?)\s*%', 10),
        ]
        if metal in {'Gold', 'Silver', 'Platinum'}:
            grade = r'(999(?:\.9)?|995|950|925|916|900|750|585)'
            patterns += [
                (r'(?<![\d.])' + grade + r'\s*(?:fine\s+)?' + alias + r'(?!\w)', 1),
                (r'(?<!\w)' + alias + r'\s*(?:fineness\s*)?[:=-]?\s*' + grade + r'(?![\d.]|\s*(?:g|gm|grams?|kg|mm|cm)\b)', 1),
            ]
        if len(metals) == 1 and metal not in ALLOYS:
            patterns += [(r'\b(?:purity|fineness|pure)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*%', 10)]
        for pattern, scale in patterns:
            for match in re.finditer(pattern, text, re.I):
                claims.append({'metal': metal, 'purity': float(match[1]) * scale, 'evidence': match[0]})
        if metal == 'Gold':
            for match in re.finditer(r'(?<!\d)(24|22|18|14)\s*(?:k|kt|karat|carat)\s*(?:gold)?\b', text, re.I):
                claims.append({'metal': metal, 'purity': {'24':999, '22':916, '18':750, '14':585}[match[1]], 'evidence': match[0]})
    return list({(c['metal'], c['purity'], c['evidence']): c for c in claims}.values())


def metal_estimate(p, rates, *, rate_metadata=None, benchmark_metadata=None):
    """Return an evidence-labelled estimate or explicit non-estimable status."""
    fields = {k: str(p.get(k) or '') for k in ('name', 'material', 'weightSize', 'subtitle', 'specificationEvidence')}
    text = ' '.join(fields.values())
    # Material is the best field, but plating/composite warnings inspect all text.
    identity = fields['material'] + ' ' + fields['name'] + ' ' + fields['specificationEvidence']
    metals = [name for name, pattern in ALIASES.items()
              if re.search(r'(?<!\w)(?:' + pattern + r')(?!\w)', identity, re.I)]
    if not metals:
        return None
    plated = bool(re.search(r'\b(?:plat(?:ed|ing)|coat(?:ed|ing)|gold[ -]filled|vermeil|silver[ -]tone|gold[ -]tone)\b', text, re.I))
    metal = metals[0] if len(metals) == 1 else ' / '.join(metals)
    result = {'metal': metal, 'detectedMetals': metals, 'materialKind': 'alloy' if any(m in ALLOYS for m in metals) else 'metal',
              'purityBasis': 'unknown', 'status': 'weight_missing', 'calculationState': 'unavailable',
              'missingEvidence': ['net metal weight'], 'taxBasis': 'unknown',
              'evidence': {k: v for k, v in fields.items() if v},
              'caveat': 'Seller claims are not independently assayed. Retail residual is not a making-charge quote.'}
    if 'Mercury' in metals:
        result['safetyNote'] = 'Parad is a seller material claim; mercury content and binding composition are unverified. No handling-safety inference.'
    claims = purity_claims(text, metals)
    result['purityClaims'] = claims
    conflict = any(len({c['purity'] for c in claims if c['metal'] == m}) > 1 for m in metals)
    invalid = any(not 0 < c['purity'] <= 1000 for c in claims)
    purity = None
    if len(metals) == 1 and metal not in ALLOYS and claims and not conflict and not invalid:
        purity = claims[0]['purity']
        result.update(purity=round(purity, 3), purityBasis='seller_claim')
    if claims and (len(metals) > 1 or any(m in ALLOYS for m in metals)):
        result['purityScope'] = 'ingredient_claims_not_alloy_proportions'
    if conflict or invalid:
        return unavailable(result, 'purity_conflict', 'consistent valid metal purity')
    if plated:
        result.update(materialKind='plated')
        result.pop('purity', None)
        result['purityBasis'] = 'unknown'
        if claims: result['purityScope'] = 'component_claims_not_finished_purity'
        return unavailable(result, 'plated_or_coated', 'separate base and coating weights', 'alloy composition' if any(m in ALLOYS for m in metals) else 'solid-metal composition')
    if len(metals) > 1:
        result.update(materialKind='mixed')
        return unavailable(result, 'composition_unknown', 'alloy composition', 'net metal weight')
    # Only accept a complete alternating size/weight sequence; do not guess
    # associations in flattened, reordered or component-weight evidence.
    pair = r'(\d+(?:\.\d+)?\s*(?:inches|inch|mm|cm))\s*;\s*(' + WEIGHT + r')'
    variant_text = fields['weightSize'].strip()
    paired = list(re.finditer(pair, variant_text, re.I))
    remainder = re.sub(pair, '', variant_text, flags=re.I).strip(' ;')
    if len(paired) > 1 and not remainder and len({m[1].lower() for m in paired}) == len(paired):
        variants = []
        for match in paired:
            child = dict(p, weightSize=match[2], regular=None, sale=None)
            estimate = metal_estimate(child, rates, rate_metadata=rate_metadata, benchmark_metadata=benchmark_metadata)
            variants.append(dict(size=match[1], **estimate))
        result['variants'] = variants
        if all(v['status'] == 'estimated' for v in variants):
            result.update(status='variant_estimates', calculationState='conditional',
                          missingEvidence=['price for each size', 'confirmation of per-piece or per-pair weight'],
                          metalValueRange=[min(v['metalValue'] for v in variants), max(v['metalValue'] for v in variants)])
            return result
    # Do not silently choose the minimum of variant, gross and shipping weights.
    weight_text = fields['weightSize'] or text
    matches = list(re.finditer(WEIGHT, weight_text, re.I))
    weights = {round(float(m[1].replace(',', '')) * (1000 if m[2].lower().startswith('k') else 1), 6) for m in matches}
    ranged = bool(re.search(r'\d\s*(?:[-–—/]|to|±)\s*\d', weight_text))
    gross = bool(re.search(r'\bgross\b|\b(?:shipping|packed|package)\s+weight\b', text, re.I))
    qualified = bool(re.search(r'\b(?:up to|at least|minimum|maximum|between)\b|[<>≤≥]', weight_text, re.I))
    ranged = ranged or bool(re.search(r'\d+(?:\.\d+)?\s*(?:[-–—]|to|±)\s*\d+(?:\.\d+)?\s*(?:kg|grams?|gms?|g)\b', text, re.I))
    qualified = qualified or bool(re.search(r'\b(?:up to|at least|minimum|maximum)\s*(?:weight\s*[:=-]?\s*)?\d+(?:\.\d+)?\s*(?:kg|grams?|gms?|g)\b', text, re.I))
    if ranged or qualified or len(weights) > 1:
        return unavailable(result, 'weight_ambiguous', 'one stated net metal weight')
    if not weights or not 0 < next(iter(weights)) <= 100000:
        return result
    weight = next(iter(weights))
    result.update(weightGrams=weight, weightBasis='seller_claim', weightEvidence=matches[0][0])
    if gross or re.search(r'\b(?:stone|stones|wood|wooden|rosewood|rudraksha|beads|gemstone|crystal|diamond|ruby|emerald|sapphire|pearl|filled)\b', text, re.I):
        return unavailable(result, 'net_metal_weight_unknown', 'net metal weight excluding non-metal parts')
    multiple = bool(re.search(r'\b(?:\d*\s*(?:pair|set|pack)|(?:[2-9]|[1-9]\d+)\s*(?:pieces?|pcs))\b', fields['name'], re.I))
    total_basis = bool(re.search(r'\b(?:total|combined|set|pair)\s*(?:net\s*)?(?:metal\s*)?weight\b|\bweight\b[^.;]{0,20}\b(?:per pair|per set|total)\b', text, re.I))
    for match in re.finditer(WEIGHT + r'\s*\(\s*(pair|1\s*set|\d+\s*pieces?)\s*\)', text, re.I):
        basis = match[3].lower().replace(' ', '')
        if basis == 'pair' and re.search(r'\bpair\b', fields['name'], re.I):
            total_basis = True
        elif basis == '1set' and re.search(r'\b(?:1\s*)?set\b', fields['name'], re.I):
            total_basis = True
        elif re.match(r'\d+pieces?', basis):
            count = re.match(r'\d+', basis)[0]
            if re.search(r'\b' + count + r'\s*pieces?\b', fields['name'], re.I):
                total_basis = True
    if multiple and not total_basis:
        return unavailable(result, 'quantity_basis_unknown', 'confirmation whether weight is per piece or for the complete set')
    if metal in ALLOYS:
        return unavailable(result, 'composition_unknown', 'alloy composition')
    if purity is None:
        return unavailable(result, 'purity_unknown', 'stated metal purity')
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
            if benchmark_metadata:
                result.update(rateDate=benchmark_metadata.get('date'), rateSource=benchmark_metadata.get('source'))
    if per_gram is None:
        return unavailable(result, 'rate_missing', 'validated reference rate')
    value = weight * per_gram
    result.update(status='estimated', calculationState='available', missingEvidence=[], ratePerGram=round(per_gram, 4), metalValue=round(value, 2), currency='INR', fineMetalGrams=round(weight * purity / 1000, 6))
    listed = number(p.get('sale') if p.get('sale') is not None else p.get('regular'))
    if listed is not None and listed >= 0 and p.get('currency', 'INR') == 'INR':
        result.update(listedPrice=listed, retailResidual=round(listed-value, 2),
                      metalSharePct=round(100*value/listed, 1) if listed else None)
        # Tax decomposition only from explicit product-specific evidence.
        tax = number(p.get('taxRatePct'))
        if p.get('taxIncluded') is True and tax is not None and 0 <= tax <= 100 and p.get('taxSource'):
            pretax = listed/(1+tax/100)
            result.update(estimatedGstIncluded=round(listed-pretax, 2), nonMetalPremiumPreTax=round(pretax-value, 2), taxBasis='product_evidence')
    return result
