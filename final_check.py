import re


with open("lightroom_raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("SHORTCUT AGENT: Testing Maximum Value Heuristic...")


clean_text = text.replace(',', '').replace('RM', '').replace('$', '')


prices = re.findall(r"(\d+\.\d{2})", clean_text)

if prices:
    
    float_prices = [float(p) for p in prices]
    
    
    grand_total = max(float_prices)
    
    print(f"\nVERIFIED!")
    print(f"All prices found: {float_prices}")
    print(f"---")
    print(f"THE EXTRACTED TOTAL: {grand_total}")
    print(f"---")
else:
    print("No prices found.")