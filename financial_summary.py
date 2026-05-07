import pandas as pd

def generate_summary():
    file_path = 'D:/Agentic_OCR/master_report.csv'
    df = pd.read_csv(file_path)

    total_spent = df['total'].sum()
    total_tax = df['tax'].sum()
    verified_count = len(df[df['status'] == 'VERIFIED'])
    errors_count = len(df[df['status'] == 'MATH_ERROR'])

    print("\n" + "="*40)
    print("AGENTIC FINANCIAL SUMMARY")
    print("="*40)
    print(f"Total Spend Found:   RM {total_spent:.2f}")
    print(f"Total Tax Paid:    RM {total_tax:.2f}")
    print(f"Verified Receipts: {verified_count}")
    print(f"Flagged for Review: {errors_count}")
    print("="*40)
    
    if errors_count > 0:
        print("\n🔎 Files needing review:")
        error_files = df[df['status'] == 'MATH_ERROR']['filename'].tolist()
        for f in error_files:
            print(f" - {f}")

if __name__ == "__main__":
    generate_summary()