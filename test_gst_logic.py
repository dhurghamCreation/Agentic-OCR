import re

# Load the Lightroom text we saved earlier
with open("lightroom_raw.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

print("🔬 TESTING SMART GST AUDITOR...")

# 1. Extract all prices
clean_text = full_text.replace(',', '').replace('RM', '').replace('$', '')
prices = [float(p) for p in re.findall(r"(\d+\.\d{2})", clean_text)]

if prices:
    total = max(prices)
    tax_found = False
    
    
    expected_tax_incl = total * (6 / 106)
    expected_tax_excl = (total / 1.06) * 0.06

    print(f"Grand Total Found: {total}")
    print(f"Target Tax (Approx): {expected_tax_incl:.2f} or {expected_tax_excl:.2f}")

    for p in prices:
        
        if p != total and (abs(p - expected_tax_incl) < 0.50 or abs(p - expected_tax_excl) < 0.50):
            print(f"MATCH FOUND! Tax is: {p}")
            subtotal = round(total - p, 2)
            print(f"Result: Subtotal({subtotal}) + Tax({p}) = Total({total})")
            tax_found = True
            break

    if not tax_found:
        print("GST Match not found in the numbers.")