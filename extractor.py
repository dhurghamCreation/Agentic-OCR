import os
import glob
import re
import csv
from docling.document_converter import DocumentConverter

def agent_extract_data(image_path):
    print(f"\n🧠 AGENT_THOUGHT: Extracting data from {os.path.basename(image_path)}...")
    try:
        converter = DocumentConverter()
        result = converter.convert(image_path)
        
        extracted_data = {
            "vendor": "Unknown",
            "date": "Unknown",
            "total": "0.00",
            "filename": os.path.basename(image_path)
        }

        # 1. SMART VENDOR LOOKUP: Skip pictures/tables and find the first TEXT item
        for item, _ in result.document.iterate_items():
            if hasattr(item, 'text') and item.text.strip():
                # The first non-empty text is usually the Vendor Name
                extracted_data["vendor"] = item.text.strip()
                break

        # 2. Use Markdown export for pattern matching
        full_text = result.document.export_to_markdown()
        
        # Find Date (Matches DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY)
        date_pattern = r"(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})"
        date_match = re.search(date_pattern, full_text)
        if date_match:
            extracted_data["date"] = date_match.group(1)

        # Find Total (Improved pattern to handle spaces and different symbols)
        # Look for 'total' followed by a number like 123.45
        total_pattern = r"total.*?([\d,]+\.\d{2})"
        total_matches = re.findall(total_pattern, full_text.lower())
        if total_matches:
            extracted_data["total"] = total_matches[-1]

        print(f"📊 RESULT: {extracted_data}")
        return extracted_data

    except Exception as e:
        print(f"⚠️ Agent encountered an issue with {os.path.basename(image_path)}: {e}")
        return {"vendor": "ERROR", "date": "ERROR", "total": "0.00", "filename": os.path.basename(image_path)}

# --- RUN BULK PROCESSOR ---
search_pattern = "D:/Agentic_OCR/data/sroie/**/*.jpg"
all_images = glob.glob(search_pattern, recursive=True)[:10] 

results = []
for img in all_images:
    data = agent_extract_data(img)
    results.append(data)

# Save to CSV
output_file = 'D:/Agentic_OCR/final_report.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["filename", "vendor", "date", "total"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n🚀 MISSION ACCOMPLISHED: Processed {len(results)} files.")
print(f"📂 Report saved to: {output_file}")