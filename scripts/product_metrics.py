"""Cautious display-only price metrics; never substitute for a material quote."""
import re

STONE = re.compile(r'gemstone|diamond|sapphire|emerald|ruby|opal|citrine|amethyst|garnet|turquoise|zircon|topaz|quartz|peridot', re.I)
CARAT = re.compile(r'(?<![\d.])(\d+(?:\.\d+)?)\s*(?:carats?|ct)\b', re.I)
RANGE = re.compile(r'\d+(?:\.\d+)?\s*(?:to|[-–—/])\s*\d+(?:\.\d+)?', re.I)

def product_asking_per_carat(name, category, weight_size, listed):
    if listed is None or not STONE.search(f'{category} {name}'):
        return None
    # A range in the title may be collapsed into just its upper end in an
    # extracted size field. Never present that as a single stone weight.
    if RANGE.search(f'{name} {weight_size}'):
        return None
    weights = CARAT.findall(weight_size)
    if len(weights) != 1 or float(weights[0]) <= 0:
        return None
    return {'amount': round(listed / float(weights[0]), 2), 'unit': 'carat',
            'basis': 'listed product price divided by stated stone carats; may include a setting, not a gemstone valuation'}
