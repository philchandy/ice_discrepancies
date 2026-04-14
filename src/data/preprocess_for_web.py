"""
Preprocess ICE detention-stays data into a compact JSON for the web visualization.
Source data: https://www.ice.gov/open-data/detention-stays
"""

import json
import math
from pathlib import Path

import pandas as pd

# ── paths ──────────────────────────────────────────────────────────────────────
BASE        = Path(__file__).parent
STAYS_CSV   = BASE / "deportation_data_project_src" / "detention-stays-latest.csv"
LOOKUP_CSV  = BASE / "lookups" / "factory_code_map_with_coordinates.csv"
OUTPUT_JSON = BASE.parent.parent / "public" / "data" / "processedData.json"

SAMPLE_SIZE = 100_000
RANDOM_SEED = 42

# ── region lookup ──────────────────────────────────────────────────────────────
_MEXICO = {"MEXICO"}
_CENTRAL = {
    "HONDURAS", "GUATEMALA", "EL SALVADOR", "NICARAGUA",
    "COSTA RICA", "PANAMA", "BELIZE",
}
_CARIBBEAN = {
    "CUBA", "HAITI", "DOMINICAN REPUBLIC", "JAMAICA",
    "TRINIDAD AND TOBAGO", "BARBADOS", "BAHAMAS", "GUADELOUPE",
    "SAINT LUCIA", "GRENADA", "MARTINIQUE", "ANTIGUA AND BARBUDA",
    "SAINT KITTS AND NEVIS", "SAINT VINCENT AND THE GRENADINES",
    "DOMINICA", "CAYMAN ISLANDS", "TURKS AND CAICOS ISLANDS",
}
_SOUTH = {
    "COLOMBIA", "VENEZUELA", "ECUADOR", "PERU", "BRAZIL",
    "BOLIVIA", "CHILE", "ARGENTINA", "PARAGUAY", "URUGUAY",
    "GUYANA", "SURINAME",
}
_AFRICA = {
    "NIGERIA", "ETHIOPIA", "GHANA", "KENYA", "CAMEROON", "SENEGAL",
    "IVORY COAST", "COTE D'IVOIRE", "GUINEA", "SIERRA LEONE", "LIBERIA",
    "ANGOLA", "MOZAMBIQUE", "TOGO", "BENIN", "MALI", "BURKINA FASO",
    "NIGER", "CHAD", "SOMALIA", "ERITREA", "SUDAN", "SOUTH SUDAN",
    "CONGO", "DEMOCRATIC REPUBLIC OF THE CONGO", "REPUBLIC OF THE CONGO",
    "GABON", "EQUATORIAL GUINEA", "CENTRAL AFRICAN REPUBLIC", "TANZANIA",
    "ZIMBABWE", "ZAMBIA", "MALAWI", "RWANDA", "BURUNDI", "MAURITIUS",
    "MADAGASCAR", "CAPE VERDE", "SAO TOME AND PRINCIPE", "GAMBIA",
    "GUINEA BISSAU", "DJIBOUTI", "COMOROS", "SEYCHELLES", "SOUTH AFRICA",
    "NAMIBIA", "BOTSWANA", "LESOTHO", "SWAZILAND", "EGYPT", "LIBYA",
    "ALGERIA", "MOROCCO", "TUNISIA",
}


def _region(country):
    c = str(country).strip().upper()
    if c in _MEXICO:    return "Mexico"
    if c in _CENTRAL:   return "Central America"
    if c in _CARIBBEAN: return "Caribbean"
    if c in _SOUTH:     return "South America"
    if c in _AFRICA:    return "Africa"
    if c in ("", "NAN", "NOT APPLICABLE", "UNKNOWN", "STATELESS"):
        return "Unknown"
    return "Asia/Other"


def _age_group(birth_year, booking_year):
    try:
        age = int(booking_year) - int(float(birth_year))
    except (ValueError, TypeError):
        return "Unknown"
    if age < 18:  return "Under 18"
    if age < 25:  return "18-24"
    if age < 35:  return "25-34"
    if age < 45:  return "35-44"
    if age < 55:  return "45-54"
    return "55+"


def _criminal(criminality, felon):
    crim = str(criminality).strip()
    if crim.startswith("1 Convicted") or crim.startswith("5 Gang"):
        return "Felony"
    if crim.startswith("2 Pending"):
        return "Misdemeanor"
    return "None"


_PROGRAM_MAP = {
    "Border Patrol":                           "Border Patrol",
    "ERO Criminal Alien Program":              "Criminal Referral",
    "ERO Non-Criminal Alien Program":          "ICE Arrest",
    "Non-Criminal Alien Removal Program":      "ICE Arrest",
    "Asylum":                                  "Asylum Intake",
    "Parole":                                  "Asylum Intake",
}


def _program(p):
    p = str(p).strip()
    if p in _PROGRAM_MAP:
        return _PROGRAM_MAP[p]
    if "Criminal Alien" in p:
        return "Criminal Referral"
    if "Non-Criminal" in p:
        return "ICE Arrest"
    if p and p.lower() not in ("nan",):
        return p
    return "Unknown"


def _outcome(release_reason):
    r = str(release_reason).strip()
    if not r or r.lower() in ("nan",):
        return "Still Detained"
    rl = r.lower()
    if "removed" in rl or "voluntary return" in rl or "deported" in rl:
        return "Removed"
    if ("bond" in rl or "recognizance" in rl or "released" in rl
            or "humanitarian" in rl or "paroled" in rl or "supervision" in rl):
        return "Released"
    if "transfer" in rl:
        return "Transferred"
    return "Released"


def _length_days(book_in, book_out):
    try:
        d_in  = pd.to_datetime(book_in,  utc=True, errors="raise")
        d_out = pd.to_datetime(book_out, utc=True, errors="raise")
        return max(0, (d_out - d_in).days)
    except Exception:
        return None


def _transfer_type(n_stints):
    try:
        return "No Transfer" if int(n_stints) <= 1 else "Transferred"
    except (ValueError, TypeError):
        return "Unknown"

def main():
    print("Reading stays CSV …")
    df = pd.read_csv(STAYS_CSV, low_memory=False)
    print(f"  {len(df):,} rows loaded")

    # booking year
    df["_year"] = (
        pd.to_datetime(df["stay_book_in_date_time"], utc=True, errors="coerce")
        .dt.year
    )

    ts = (
        df.groupby("_year")
          .size()
          .reset_index(name="population")
          .dropna(subset=["_year"])
    )
    time_series = [
        {"year": int(r["_year"]), "population": int(r["population"])}
        for _, r in ts.iterrows()
        if not math.isnan(r["_year"])
    ]
    time_series.sort(key=lambda x: x["year"])
    print(f"  Time series spans {time_series[0]['year']}–{time_series[-1]['year']}")

    #full facility counts (for map scaling)
    fac_counts = df["detention_facility_code_first"].value_counts()

    print("Reading facility lookup …")
    lookup = pd.read_csv(LOOKUP_CSV, low_memory=False, encoding="latin-1")
    lookup = lookup.rename(columns={
        "code": "facility_id",
        "name": "facility_name",
        "latitude":  "lat",
        "longitude": "lng",
    })
    lookup = (
        lookup[["facility_id", "facility_name", "lat", "lng"]]
        .dropna(subset=["lat", "lng"])
        .drop_duplicates(subset="facility_id")
    )
    lookup["facility_id"] = lookup["facility_id"].str.strip()

    facilities = []
    for code, count in fac_counts.items():
        row = lookup[lookup["facility_id"] == str(code).strip()]
        if row.empty:
            continue
        r = row.iloc[0]
        try:
            lat, lng = float(r["lat"]), float(r["lng"])
        except (ValueError, TypeError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            continue
        facilities.append({
            "facility_id": str(code),
            "name":        str(r["facility_name"]),
            "lat":         lat,
            "lng":         lng,
            "count":       int(count),
        })
    facilities.sort(key=lambda x: -x["count"])
    print(f"  {len(facilities):,} facilities with coordinates")

    #sample records for web (schema-mapped + filtered for null booking year)
    print(f"Sampling {SAMPLE_SIZE:,} records …")
    sample = df.sample(min(SAMPLE_SIZE, len(df)), random_state=RANDOM_SEED)

    records = []
    for _, row in sample.iterrows():
        by = row.get("_year")
        length = _length_days(
            row.get("stay_book_in_date_time"),
            row.get("stay_book_out_date_time"),
        )
        if pd.isna(by):
            continue
        records.append({
            "sex":                   str(row.get("gender", "")).strip() or "Unknown",
            "age_group":             _age_group(row.get("birth_year"), by),
            "region_of_origin":      _region(row.get("citizenship_country")),
            "criminal_history":      _criminal(
                row.get("book_in_criminality"), row.get("felon")
            ),
            "first_booking_type":    _program(row.get("final_program")),
            "transfer_type":         _transfer_type(row.get("n_stints")),
            "outcome":               _outcome(row.get("stay_release_reason")),
            "detention_length_days": length,
            "booking_year":          int(by),
            "facility_id":           str(row.get("detention_facility_code_first", "")).strip() or "Unknown",
        })

    print(f"  {len(records):,} records after filtering nulls")

    #output json 
    out = {"records": records, "timeSeries": time_series, "facilities": facilities}
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))

    mb = OUTPUT_JSON.stat().st_size / 1_048_576
    print(f"\n✓  Wrote {OUTPUT_JSON.name}  ({mb:.1f} MB, {len(records):,} records, "
          f"{len(facilities):,} facilities)")


if __name__ == "__main__":
    main()
