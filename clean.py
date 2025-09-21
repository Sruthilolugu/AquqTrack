import pandas as pd
import re

# Load your current text file
with open("/Users/sruthiuma/Documents/fold2/dataset1.txt", "r") as f:
    lines = f.readlines()

cleaned_rows = []

for line in lines[1:]:  # skip header if present
    line = line.strip()
    # Match last 4 numeric/date fields
    match = re.match(r'^(.*)\s+([\d.]+)\s+([\d.]+)\s+(\d{2}-\d{2}-\d{2})\s+([\d.]+)$', line)
    if match:
        text_part, lat, lon, date, dtwl = match.groups()
        text_fields = text_part.split()
        # STATE_UT: first 2 words
        STATE_UT = " ".join(text_fields[:2])
        # BLOCK: second-to-last text field
        BLOCK = text_fields[-2]
        # VILLAGE: last text field
        VILLAGE = text_fields[-1]
        # DISTRICT: everything in between
        DISTRICT = " ".join(text_fields[2:-2])
        cleaned_rows.append([STATE_UT, DISTRICT, BLOCK, VILLAGE, lat, lon, date, dtwl])

# Create DataFrame
df = pd.DataFrame(cleaned_rows, columns=[
    "STATE_UT","DISTRICT","BLOCK","VILLAGE","LATITUDE","LONGITUDE","Date","DTWL"
])

# Convert numeric/date columns
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"])
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"])
df["DTWL"] = pd.to_numeric(df["DTWL"])
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%y")

# Save as CSV
df.to_csv("monsoon_cleaned.csv", index=False)

print("✅ Saved as monsoon_cleaned.csv")
print(df.head())
