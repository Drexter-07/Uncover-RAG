import json

# Load the messy data
with open("clean_treatment.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Original count: {len(data)} pages")

# FILTER LOGIC
clean_data = []
for item in data:
    url = item.get("source", "")
    title = item.get("title", "").lower()
    
    # 1. Exclude Blog Posts (URLs containing /post/)
    if "/post/" in url:
        continue
        
    # 2. Exclude "Home Remedies" if they slipped through
    if "home remedies" in title or "natural remedies" in title:
        continue

    # 3. Keep everything else (Treatments, Concerns)
    clean_data.append(item)

print(f"Cleaned count: {len(clean_data)} pages")

# Save the clean file
with open("treatments.json", "w", encoding="utf-8") as f:
    json.dump(clean_data, f, indent=2, ensure_ascii=False)

print("✅ Success! Created treatments.json with only clinical data.")