
import sqlite3
import pandas as pd
import os

print("=" * 60)
print("SCHOOL OF DANDORI - DATA VALIDATION & DATABASE LOADER")
print("=" * 60)

# ──────────────────────────────────────────────
# STEP 1: READ THE CSV DATA
# ──────────────────────────────────────────────
print("\n📂 Reading courses.csv...")
df = pd.read_csv("../courses.csv")
print(f"✅ Loaded {len(df)} courses from CSV")

# ──────────────────────────────────────────────
# STEP 2: VALIDATE THE DATA
# ──────────────────────────────────────────────
print("\n🔍 Validating data quality...")

issues = []

# Check for missing values
missing_titles = df['title'].isna().sum()
missing_instructors = df['instructor'].isna().sum()
missing_locations = df['location'].isna().sum()
missing_costs = df['cost'].isna().sum()

if missing_titles > 0:
    issues.append(f"⚠️  {missing_titles} courses missing title")
if missing_instructors > 0:
    issues.append(f"⚠️  {missing_instructors} courses missing instructor")
if missing_locations > 0:
    issues.append(f"⚠️  {missing_locations} courses missing location")
if missing_costs > 0:
    issues.append(f"⚠️  {missing_costs} courses missing cost")

# Check cost range
if df['cost'].notna().any():
    min_cost = df['cost'].min()
    max_cost = df['cost'].max()
    print(f"   Cost range: £{int(min_cost)} - £{int(max_cost)}")
    
    # Flag unusual costs
    if min_cost < 40:
        issues.append(f"⚠️  Unusually low cost detected: £{int(min_cost)}")
    if max_cost > 150:
        issues.append(f"⚠️  Unusually high cost detected: £{int(max_cost)}")

# Check for duplicates
duplicates = df[df.duplicated(subset=['title'], keep=False)]
if not duplicates.empty:
    issues.append(f"⚠️  {len(duplicates)} potential duplicate titles found")

# Print validation results
if issues:
    print("\n⚠️  Issues found:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("✅ All validation checks passed!")

complete_rows = df.dropna().shape[0]
print(f"\n📊 Summary:")
print(f"   Total courses: {len(df)}")
print(f"   Complete rows: {complete_rows}")
print(f"   Incomplete rows: {len(df) - complete_rows}")

# ──────────────────────────────────────────────
# STEP 3: CONNECT TO DATABASE
# ──────────────────────────────────────────────
print("\n🗄️  Connecting to database...")
db_path = "../database/db.sqlite"
conn = sqlite3.connect(db_path)
print(f"✅ Connected to {db_path}")

# ──────────────────────────────────────────────
# STEP 4: CREATE TABLE FROM SCHEMA
# ──────────────────────────────────────────────
print("\n🏗️  Creating database schema...")
schema_path = "../database/schema.sql"

with open(schema_path, "r") as f:
    schema_sql = f.read()
    conn.executescript(schema_sql)
    
print("✅ Table 'courses' created successfully")

# ──────────────────────────────────────────────
# STEP 5: LOAD DATA INTO DATABASE
# ──────────────────────────────────────────────
print("\n💾 Loading data into database...")
df.to_sql("courses", conn, if_exists="replace", index=False)
print(f"✅ Loaded {len(df)} courses into database")

# ──────────────────────────────────────────────
# STEP 6: VERIFY THE DATA WAS LOADED
# ──────────────────────────────────────────────
print("\n✓ Verifying database contents...")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM courses")
count = cursor.fetchone()[0]
print(f"✅ Database contains {count} courses")

# Show a sample
cursor.execute("SELECT title, instructor, location, cost FROM courses LIMIT 3")
print("\n📋 Sample data from database:")
for row in cursor.fetchall():
    print(f"   • {row[0]} - {row[1]} ({row[2]}) - £{row[3]}")

conn.close()

print("\n" + "=" * 60)
print("✅ SUCCESS! Database is ready to use!")
print("=" * 60)
print("\nNext step: Run the Streamlit app with:")
print("   cd app")
print("   streamlit run main.py")