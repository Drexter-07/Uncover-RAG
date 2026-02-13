import requests
import json
import time

# --- CONFIGURATION ---
TARGET_URLS = [
    "https://uncover.co.in/concern/acne-scars",
    "https://uncover.co.in/treatment/acne-buster-peel",
    "https://uncover.co.in/treatment/anti-scar-peel",
    "https://uncover.co.in/treatment/advanced-microneedling"
]

OUTPUT_FILE = "treatments.json"

def get_clean_content_jina(url):
    jina_url = f"https://r.jina.ai/{url}"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(jina_url, headers=headers, timeout=20)
        return response.text if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def clean_content(markdown_text):
    if not markdown_text: return ""

    lines = markdown_text.split('\n')
    cleaned_lines = []
    
    # --- STEP 1: LINE-BY-LINE CLEANING ---
    for line in lines:
        # Skip Navigation Menus
        if "Hair >  BROWSE BY" in line: continue
        if "bODY >  BROWSE BY" in line: continue
        if "LASER >" in line: continue
        if "SKIN >" in line: continue
        
        # Skip "Book Appointment" & standard links
        if "[Our Locations]" in line or "[About Us]" in line or "[Media & Blog]" in line: continue
        if "[Book FREE Appointment]" in line: continue
        if "Book Appointment" in line or "Call Us Now" in line: continue
            
        # Skip Form Success Messages (New Fix)
        if "We have received your message" in line: continue
        if "success-message-icon" in line: continue
        if "Thank you! We’ll get back to you soon" in line: continue
        if "Oops! Something went wrong" in line: continue
        
        # Skip bullet points that are just links (e.g. "* [Link]")
        if line.strip().startswith("* [") and "](" in line:
            continue

        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # --- STEP 2: CUT OFF THE FOOTER ---
    # We use a list of phrases that appear at the start of the footer.
    # As soon as we see ANY of these, we delete everything after.
    cutoff_markers = [
        "Browse by Concerns", 
        "Useful Links", 
        "Copyright © Uncover",
        "Fat Loss\n\n*",       # Found in your file
        "Hair Loss & Baldness" # Found in your file
    ]
    
    cutoff_index = len(text)
    for marker in cutoff_markers:
        idx = text.find(marker)
        if idx != -1 and idx < cutoff_index:
            cutoff_index = idx
            
    # Extra safety: If "Laser Hair Removal" starts a list at the end
    # We check for the specific pattern to avoid deleting valid text about lasers.
    idx_laser = text.find("Laser Hair Removal\n\n*")
    if idx_laser != -1 and idx_laser < cutoff_index:
        cutoff_index = idx_laser

    return text[:cutoff_index].strip()

def crawl_and_extract():
    print("🚀 Starting Final Polish Scraper...")
    all_data = []

    for i, link in enumerate(TARGET_URLS):
        print(f"[{i+1}/{len(TARGET_URLS)}] Scraping: {link}")
        
        raw_markdown = get_clean_content_jina(link)
        
        if raw_markdown:
            clean_text = clean_content(raw_markdown)
            title = link.split("/")[-1].replace("-", " ").title()
            
            if len(clean_text) < 100:
                print("   ⚠️ Warning: Content seems very short.")

            entry = {
                "source": link,
                "title": title,
                "page_content": clean_text
            }
            all_data.append(entry)
            print(f"   ✅ Success! (Cleaned length: {len(clean_text)} chars)")
        else:
            print("   ❌ Failed to retrieve.")
        
        time.sleep(1.5)

    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("✅ Done.")

if __name__ == "__main__":
    crawl_and_extract()