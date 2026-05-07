import pandas as pd
import os
import glob

def run_search():
    csv_file = 'D:/Agentic_OCR/final_report.csv'
    
    if not os.path.exists(csv_file):
        print("Error: No report found. Run 'python extractor.py' first!")
        return

    
    df = pd.read_csv(csv_file)

    print("\n" + "="*30)
    print("RECEIPT SEARCH AGENT")
    print("="*30)
    query = input("Enter a keyword (Vendor or Date): ").strip().lower()

    
    
    mask = (df['vendor'].str.lower().str.contains(query, na=False)) | \
           (df['date'].str.lower().str.contains(query, na=False))
    
    results = df[mask]

    if not results.empty:
        print(f"\nFound {len(results)} matching record(s):")
        print("-" * 50)
        
        for index, row in results.iterrows():
            
            display_vendor = (row['vendor'][:40] + '..') if len(row['vendor']) > 40 else row['vendor']
            print(f"Vendor: {display_vendor}")
            print(f"Date:   {row['date']}")
            print(f"Total:  {row['total']}")
            print(f"File:   {row['filename']}")
            print("-" * 50)
        
        
        choice = input("\nWould you like to open the first matching image? (y/n): ")
        if choice.lower() == 'y':
            img_name = results.iloc[0]['filename']
            
            img_search = glob.glob(f"D:/Agentic_OCR/data/sroie/**/{img_name}", recursive=True)
            if img_search:
                print(f"Opening {img_name}...")
                os.startfile(img_search[0])
            else:
                print("Could not locate the original image file.")
    else:
        print(f"No records found for '{query}'.")

if __name__ == "__main__":
    run_search()