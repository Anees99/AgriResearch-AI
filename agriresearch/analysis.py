"""Allowlisted calculations; no generated code, query expressions or SQL."""
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

INDICATORS = {"yield": "AG.YLD.CREL.KG", "production": "AG.PRD.CREL.MT", "land": "AG.LND.CREL.HA"}
UNITS = {"yield": "kg/ha", "production": "metric tonnes", "land": "hectares"}

class DatasetTool:
    def __init__(self, path, expected_sha256=None):
        self.path = Path(path)
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        if expected_sha256 and self.sha256 != expected_sha256:
            raise ValueError("Dataset snapshot hash mismatch; review source changes before analysis")
        self.frame = pd.read_csv(path)
        required = {"country", "year", "indicator", "value"}
        if not required <= set(self.frame.columns):
            raise ValueError(f"Missing fields: {sorted(required - set(self.frame.columns))}")
        self.frame["year"] = pd.to_numeric(self.frame.year, errors="raise").astype(int)
        self.frame["value"] = pd.to_numeric(self.frame.value, errors="raise")
        if np.isinf(self.frame.value.dropna()).any() or (self.frame.value.dropna() < 0).any():
            raise ValueError("Agricultural values must be finite and nonnegative")
        if self.frame.duplicated(["country", "year", "indicator"]).any():
            raise ValueError("Duplicate country-year-indicator rows")

    def run(self, operation="summary", country="Pakistan", variable="yield", years=None):
        if operation not in {"summary", "yoy", "trend", "quality", "regions"}:
            raise ValueError("Unsupported operation")
        if variable not in INDICATORS:
            raise ValueError(f"Variable unavailable: {variable}; available: {list(INDICATORS)}")
        f = self.frame[self.frame.indicator == INDICATORS[variable]].copy()
        if operation != "regions":
            if country not in set(self.frame.country):
                raise ValueError("Country unavailable; no district or provincial measurements")
            f = f[f.country == country]
        if years:
            if not all(isinstance(y, int) and 1900 <= y <= 2100 for y in years):
                raise ValueError("Invalid years")
            missing_years = sorted(set(years) - set(f.year))
            if missing_years:
                raise ValueError(f"Requested years unavailable: {missing_years}")
            f = f[f.year.isin(years)]
        f = f.sort_values(["country", "year"])
        valid = f.dropna(subset=["value"])
        if valid.empty:
            raise ValueError("No observations for requested filters")
        records = valid.to_dict("records")
        if operation == "summary":
            result = {"n": len(valid), "mean": float(valid.value.mean()),
                      "min": float(valid.value.min()), "max": float(valid.value.max())}
        elif operation == "yoy":
            if len(valid) != 2 or int(valid.year.iloc[1]) - int(valid.year.iloc[0]) != 1:
                raise ValueError("Year-over-year requires exactly two consecutive observed years")
            a, b = map(float, valid.value)
            result = {"from_year": int(valid.year.iloc[0]), "to_year": int(valid.year.iloc[1]),
                      "absolute_change": b-a, "percent_change": None if a == 0 else 100*(b-a)/a}
        elif operation == "trend":
            result = {"observations": records, "interpretation": "Descriptive series; no causal inference"}
        elif operation == "regions":
            result = {"country_means": {k: float(v) for k,v in valid.groupby("country").value.mean().items()},
                      "scope": "National countries only; means use each country's available selected years"}
        else:
            q1, q3 = valid.value.quantile([.25, .75])
            flags = valid[(valid.value < q1-1.5*(q3-q1)) | (valid.value > q3+1.5*(q3-q1))]
            result = {"missing": int(f.value.isna().sum()), "rows": len(f),
                      "iqr_outlier_flags": len(flags), "note": "Flags are not proof of measurement error"}
        return {"operation": operation, "country": country, "variable": variable, "unit": UNITS[variable],
                "result": result, "rows_used": records, "source": "World Bank WDI / FAO",
                "url": f"https://data.worldbank.org/indicator/{INDICATORS[variable]}",
                "dataset_sha256": self.sha256, "citation_id": "DATA-1"}
