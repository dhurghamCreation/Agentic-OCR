import re

# Load the saved text
with open("lightroom_raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("--- RAW TEXT FROM AI ---")
print(text)
print("--- LOGIC TEST ---")


total_pattern = r"tot.*?(?:rm|[:\s])*([\d,]+\.\d{2})"
match = re.search(total_pattern, text.lower())

if match:
    found_total = match.group(1).replace(",", "")
    print(f"SUCCESS! Found Total: {found_total}")
else:
    print("FAILED: Regex still couldn't see the total.")
    # If this fails, look at the "RAW TEXT FROM AI" printed above 
    # and tell me what the line with the total looks like.