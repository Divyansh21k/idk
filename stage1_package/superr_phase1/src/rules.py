"""Shared analysis rules (single source of truth for Step 1 onwards). Every rule is documented in decision_log.md / technical_methodology.md."""
import re
import numpy as np, pandas as pd

ILLEGAL_KINDS = ('wide', 'overstep', 'other')       # D07: delivery does not consume a legal ball
NB_LIKE = ('overstep', 'other')                      # D08/A1: no-ball-like deliveries (free hit follows)
CREDIT_TYPES = ('Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket')   # D12 [KNOW convention]
EXTRAS_TO_KIND = {'wide': 'wide', 'Overstep': 'overstep', 'other': 'other'}
REVISED_DQ = (14130, 20190)                          # D06 data-quality exclusions
MINOR_FLAG = (14164, 41509)                          # D06 retained with a flag
DLS_RE = r'D/?L|DLS'

def result_class(text):
    t = str(text).lower()
    if 'abandon' in t: return 'abandoned'
    if 'no result' in t: return 'no_result'
    if re.search(r'super\s*over|one over|eliminator', t): return 'superover_decided'
    if re.search(r'\btied?\b', t): return 'tie_no_superover'
    if re.search(r'\bwon\b', t) and re.search(r'\d+\s*(runs?|wickets?|wkts?)', t): return 'won_margin'
    return 'other'

def batting_band(order):
    return 'opener (1-2)' if order <= 2 else 'top order (3-4)' if order <= 4 else 'middle (5-6)' if order <= 6 else 'lower (7+)'

def arm_of(bowling_type):
    s = str(bowling_type).lower()
    return 'left' if 'left' in s else 'right'
