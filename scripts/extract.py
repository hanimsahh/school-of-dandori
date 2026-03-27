import pdfplumber
import pandas as pd
import os
import re

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
PDF_FOLDER = "data"          # folder containing the 211 PDFs
OUTPUT_CSV  = "courses.csv"

# All known locations used by the School of Dandori.
# Using a whitelist is far more reliable than suffix-keyword heuristics,
# especially for "Scottish Highlands", "Lake District", "Stratford-upon-Avon".
KNOWN_LOCATIONS = {
    "Bath", "Brighton", "Cambridge", "Canterbury", "Chester",
    "Cornwall", "Cotswolds", "Devon", "Durham", "Edinburgh",
    "Exeter", "Glasgow", "Harrogate", "Inverness",
    "Lake District", "Norfolk", "Northumberland", "Oxford",
    "Peak District", "Scottish Highlands", "Stratford-upon-Avon",
    "Suffolk", "Windsor", "York",
}

# Sorted longest-first so "Scottish Highlands" matches before "Highlands" etc.
KNOWN_LOCATIONS_SORTED = sorted(KNOWN_LOCATIONS, key=len, reverse=True)


def extract_location(text: str):
    """Return the first matching known location found in `text`."""
    for loc in KNOWN_LOCATIONS_SORTED:
        if loc in text:
            return loc
    return None


def extract_instructor(line: str, location: str):
    """
    Given the raw data line (e.g. 'Professor Plaid McLoom Scottish Highlands')
    and the already-extracted location, strip the location and return the rest.

    Also cleans two real dirty-data patterns found in the actual PDFs:
    - ", UK" suffix  (class_161: 'Madame Felicity Feathers , UK')
    - "Botanical Gardens" venue bleed  (class_204: 'Lady Fern Foliage  Botanical Gardens')
    Both are stripped generically rather than as hardcoded per-file patches.
    """
    if location and location in line:
        name = line.replace(location, "").strip()
    else:
        name = line.strip()

    # Remove trailing ", UK" (with optional spaces around the comma)
    name = re.sub(r"\s*,\s*UK\s*$", "", name).strip()

    # Remove trailing "Botanical Gardens" (venue text that bled into instructor field)
    name = re.sub(r"\s+Botanical Gardens\s*$", "", name).strip()

    return name or None


def parse_pdf(file_path: str) -> dict:
    """Extract title, instructor, location and cost from a single PDF."""
    result = {"title": None, "instructor": None, "location": None, "cost": None}

    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # ── Find the header line containing "Instructor" and "Location" ──
        header_idx = None
        for i, line in enumerate(lines):
            if "Instructor" in line and "Location" in line:
                header_idx = i
                break

        # ── Title: join ALL lines above the header ────────────────────────
        # BUG IN ORIGINAL: lines[0] alone misses wrapped title lines.
        # Long titles span multiple lines in the PDF; we join them all.
        if header_idx is not None and header_idx > 0:
            result["title"] = " ".join(lines[:header_idx])
        elif lines:
            result["title"] = lines[0]

        # ── Instructor + Location ─────────────────────────────────────────
        if header_idx is not None and header_idx + 1 < len(lines):
            data_line = lines[header_idx + 1]
            location = extract_location(data_line)
            result["location"] = location
            result["instructor"] = extract_instructor(data_line, location)

        # ── Cost ──────────────────────────────────────────────────────────
        cost_match = re.search(r"£(\d+)", text)
        if cost_match:
            result["cost"] = int(cost_match.group(1))

    except Exception as exc:
        print(f"  ERROR reading {os.path.basename(file_path)}: {exc}")

    return result


# ──────────────────────────────────────────────
# MAIN EXTRACTION LOOP
# ──────────────────────────────────────────────
courses = []
pdf_files = sorted(f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf"))
print(f"Found {len(pdf_files)} PDFs in '{PDF_FOLDER}'")

for filename in pdf_files:
    data = parse_pdf(os.path.join(PDF_FOLDER, filename))
    data["file"] = filename
    courses.append(data)

df = pd.DataFrame(courses, columns=["file", "title", "instructor", "location", "cost"])

# ──────────────────────────────────────────────
# VALIDATION
# ──────────────────────────────────────────────
print("\n── Validation Report ──────────────────────────────")
print("\nMissing values per column:")
print(df.isnull().sum())

if df["cost"].notna().all():
    print(f"\nCost range: £{int(df['cost'].min())} – £{int(df['cost'].max())}")
else:
    print(f"\nFiles missing cost:")
    for f in df[df["cost"].isna()]["file"].tolist():
        print(f"  {f}")

unknown_locs = df[df["location"].notna() & ~df["location"].isin(KNOWN_LOCATIONS)]
if not unknown_locs.empty:
    print(f"\nUnknown locations ({len(unknown_locs)}):")
    print(unknown_locs[["file", "location"]].to_string(index=False))
else:
    print("\nAll locations valid ✓")

print(f"\nTotal extracted : {len(df)}")
print(f"Complete rows   : {df.dropna().shape[0]}")

# ──────────────────────────────────────────────
# SAVE
# ──────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved → {OUTPUT_CSV}")
print("\nSample (first 5 rows):")
print(df.head().to_string(index=False))