import pandas as pd
import glob
import os

folder_path = r"D:\merge"

# Find all CSV files except output file
files = [
    f for f in glob.glob(os.path.join(folder_path, "*.csv"))
    if os.path.basename(f).lower() != "merged_unique.csv"
]

if not files:
    print("No CSV files found!")
    exit()

dfs = []

for file in files:
    print(f"Reading: {os.path.basename(file)}")

    try:
        df = pd.read_csv(file, dtype=str, low_memory=False)
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

if not dfs:
    print("No valid CSV files could be loaded.")
    exit()

# Merge all files
merged_df = pd.concat(dfs, ignore_index=True)

before_count = len(merged_df)

# Replace NaN with empty string
merged_df = merged_df.fillna("")

print("\nColumns Found:")
print(list(merged_df.columns))

# Detect email column automatically
EMAIL_COL = None

for col in merged_df.columns:
    if col.strip().lower() in [
        "email",
        "emails",
        "e-mail",
        "mail",
        "contact_email"
    ]:
        EMAIL_COL = col
        break

# Create email score
if EMAIL_COL:
    print(f"Email column detected: {EMAIL_COL}")

    merged_df["_email_score"] = (
        merged_df[EMAIL_COL]
        .astype(str)
        .str.strip()
        .ne("")
        .astype(int)
    )
else:
    print("No email column found.")
    merged_df["_email_score"] = 0

# Determine duplicate keys automatically
preferred_cols = ["name", "address", "phone", "website"]

KEY_COLS = [
    col for col in preferred_cols
    if col in merged_df.columns
]

# If none found, use all columns except email score
if not KEY_COLS:
    KEY_COLS = [
        col for col in merged_df.columns
        if col != "_email_score"
    ]

print(f"Using duplicate keys: {KEY_COLS}")

# Keep rows with email first
merged_df = merged_df.sort_values(
    by="_email_score",
    ascending=False
)

# Remove duplicates
merged_df = merged_df.drop_duplicates(
    subset=KEY_COLS,
    keep="first"
)

merged_df = merged_df.drop(columns=["_email_score"])

after_count = len(merged_df)

# Save result
output_file = os.path.join(folder_path, "m1erged_unique.csv")

merged_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\n========== DONE ==========")
print(f"Files Merged: {len(files)}")
print(f"Rows Before: {before_count:,}")
print(f"Rows After : {after_count:,}")
print(f"Duplicates Removed: {before_count - after_count:,}")
print(f"Saved: {output_file}")
