from docling.document_converter import DocumentConverter


path = "D:/Agentic_OCR/data/sroie/SROIE2019/test/img/X51005268275.jpg"
print("Analyzing Lightroom receipt (One-time heavy lift)...")
converter = DocumentConverter()
result = converter.convert(path)
md_text = result.document.export_to_markdown()


with open("lightroom_raw.txt", "w", encoding="utf-8") as f:
    f.write(md_text)

print("Saved raw text to 'lightroom_raw.txt'. Now we can test logic instantly.")