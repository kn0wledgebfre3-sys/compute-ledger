"""Unit conversion for the measurements table: one place, factors stated in measurement_vocab.json.

to_canonical(value, unit) -> (value_in_canonical_unit or None, canonical_unit)
A unit whose factor is null (money, ratios, intensities, concentrations) is kept as published:
the canonical value is None and the canonical unit is the published one.
"""
import json
from pathlib import Path

VOCAB = json.load(open(Path(__file__).with_name("measurement_vocab.json"), encoding="utf-8"))
UNITS = VOCAB["units"]
DIMS = VOCAB["dimensions"]


def dimension(unit: str) -> str:
    return UNITS[unit]["dimension"]


def to_canonical(value, unit: str):
    if value in (None, ""):
        return None, None
    u = UNITS[unit]
    if u["factor"] is None:
        return None, unit
    canon = DIMS[u["dimension"]]
    return round(float(value) * u["factor"], 6), canon


def fmt(x) -> str:
    """Plain decimal text without float noise: 1586892.15 stays 1586892.15, 4.0 becomes 4."""
    if x is None or x == "":
        return ""
    x = float(x)
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s
