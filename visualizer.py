import cv2
import os
import glob
from docling.document_converter import DocumentConverter

def draw_agent_vision(image_path):
    print(f"[*] AGENT_THOUGHT: Loading vision engine (Docling)...")
    
    try:
        converter = DocumentConverter()
        result = converter.convert(image_path)
        
        
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Image not found at {image_path}")
            return

        h, w, _ = image.shape
        print(f"[*] Processing {w}x{h} image pixels...")

        if not result.document.pages:
            print("AI ERROR: No pages detected. Model download might be corrupted.")
            print("Action: Run the 'Hard Reset' command provided by Gemini.")
            return

        count = 0
        for item, _ in result.document.iterate_items():
      
            if hasattr(item, 'prov') and item.prov:
                bbox = item.prov[0].bbox 
                
                
                x1, y1 = int(bbox.l), int(h - bbox.t)
                x2, y2 = int(bbox.r), int(h - bbox.b)

                # Draw GREEN box for general text
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 1)
                count += 1
                
               
                text_content = getattr(item, 'text', "").lower()
                if "total" in text_content:
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(image, "TOTAL FOUND", (x1, y1-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        output_path = "D:/Agentic_OCR/vision_map.jpg"
        cv2.imwrite(output_path, image)
        print(f"SUCCESS: Drew {count} boxes. See 'vision_map.jpg' in D:/Agentic_OCR")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")

# --- TEST ---
search_pattern = "D:/Agentic_OCR/data/sroie/**/*.jpg"
found_images = glob.glob(search_pattern, recursive=True)

if found_images:
    draw_agent_vision(found_images[0])
else:
    print("No images found in sroie folder!")