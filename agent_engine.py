import concurrent.futures
import csv
import json
import logging
import os
import re
import shutil
import threading
from datetime import datetime

try:
    from docling.document_converter import DocumentConverter
except Exception:
    DocumentConverter = None

try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] AGENT_THOUGHT: %(message)s",
    handlers=[logging.FileHandler("agent_trace.log"), logging.StreamHandler()],
)


class ReceiptAgent:
    def __init__(self, max_workers=None, ocr_engine=None, ocr_timeout_seconds=25):
        self.converter = DocumentConverter() if DocumentConverter else None
        self.max_workers = max_workers
        self.ocr_engine = (ocr_engine or "docling").lower()
        self.ocr_timeout_seconds = max(5, int(ocr_timeout_seconds or 25))
        self.patterns = {
            "date": r"(\d{2}[/\-\.]\d{2}[/\-\.]\d{2,4})",
        }

        self.processed_index_path = "D:/Agentic_OCR/processed_index.json"
        self.processed_index = self._load_processed_index()

    def _run_with_timeout(self, fn, timeout_seconds):
        result_box = {"value": None, "error": None}

        def runner():
            try:
                result_box["value"] = fn()
            except Exception as exc:
                result_box["error"] = exc

        worker = threading.Thread(target=runner, daemon=True)
        worker.start()
        worker.join(timeout_seconds)

        if worker.is_alive():
            raise TimeoutError(f"Operation timed out after {timeout_seconds}s")
        if result_box["error"]:
            raise result_box["error"]
        return result_box["value"]

    def _load_processed_index(self):
        if os.path.exists(self.processed_index_path):
            try:
                with open(self.processed_index_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_processed_index(self):
        try:
            os.makedirs(os.path.dirname(self.processed_index_path), exist_ok=True)
            with open(self.processed_index_path, "w", encoding="utf-8") as f:
                json.dump(self.processed_index, f, indent=2)
        except Exception:
            logging.exception("Failed to save processed index")

    def _collect_images(self, folder_path, limit=10):
        preferred_dirs = [
            os.path.join(folder_path, "SROIE2019", "test", "img"),
            os.path.join(folder_path, "test", "img"),
            folder_path,
        ]

        images = []
        seen = set()
        for root_dir in preferred_dirs:
            if not os.path.exists(root_dir):
                continue

            for root, _, files in os.walk(root_dir):
                for name in files:
                    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
                        continue
                    full = os.path.join(root, name)
                    if full in seen:
                        continue
                    seen.add(full)
                    images.append(full)
                    if len(images) >= limit:
                        return images
        return images

    def process_document(self, image_path):
        fname = os.path.basename(image_path)
        try:
            full_text = ""
            if "tesseract" in self.ocr_engine and pytesseract:
                try:
                    img = Image.open(image_path)
                    full_text = pytesseract.image_to_string(img)
                except Exception as e:
                    logging.warning(f"Tesseract failed for {fname}: {e}")

            if not full_text and self.converter:
                try:
                    result = self._run_with_timeout(
                        lambda: self.converter.convert(image_path),
                        self.ocr_timeout_seconds,
                    )
                    full_text = result.document.export_to_markdown()
                except TimeoutError:
                    logging.warning(
                        f"Docling timeout for {fname} after {self.ocr_timeout_seconds}s. Falling back."
                    )
                except Exception:
                    logging.exception(f"Docling converter failed for {fname}")

            if not full_text and pytesseract:
                try:
                    img = Image.open(image_path)
                    full_text = pytesseract.image_to_string(img)
                except Exception:
                    logging.exception(f"Tesseract fallback failed for {fname}")

            if not full_text:
                raise RuntimeError("No OCR output")

            data = {
                "filename": fname,
                "vendor": "Unknown",
                "date": "Unknown",
                "subtotal": 0.0,
                "tax": 0.0,
                "total": 0.0,
                "status": "Needs Review",
                "new_name": "",
            }

            lines = [l.strip() for l in full_text.split("\n") if len(l.strip()) > 3]
            if lines:
                data["vendor"] = re.sub(r"[^\w\s]", "", lines[0][:25]).strip().upper()

            date_match = re.search(self.patterns["date"], full_text)
            if date_match:
                data["date"] = date_match.group(1).replace("/", "-")

            clean_text = full_text.replace(",", "").replace("RM", "").replace("$", "")
            prices = [float(p) for p in re.findall(r"(\d+\.\d{2})", clean_text)]

            if prices:
                total = max(prices)
                data["total"] = total

                expected_tax_incl = total * (6 / 106)
                expected_tax_excl = (total / 1.06) * 0.06

                tax_found = False
                for p in prices:
                    if p == total:
                        continue
                    if abs(p - expected_tax_incl) < 0.50 or abs(p - expected_tax_excl) < 0.50:
                        data["tax"] = p
                        data["subtotal"] = round(total - p, 2)
                        data["status"] = "VERIFIED (6% GST)"
                        tax_found = True
                        break

                if not tax_found and len(prices) >= 2:
                    prices.sort()
                    data["tax"] = prices[0]
                    data["subtotal"] = round(total - prices[0], 2)
                    if abs((data["subtotal"] + data["tax"]) - total) < 0.05:
                        data["status"] = "VERIFIED (Math)"
                    else:
                        data["status"] = "MATH ERROR"

            vendor_slug = data["vendor"].replace(" ", "_")
            data["new_name"] = f"{data['date']}_{vendor_slug}_{data['total']}.jpg"
            return data
        except Exception as e:
            logging.error(f"Error processing {fname}: {e}")
            return None

    def bulk_process(
        self,
        folder_path,
        limit=10,
        report_path="D:/Agentic_OCR/master_report.csv",
        write_report=True,
        incremental=False,
        progress_callback=None,
    ):
        images = self._collect_images(folder_path, limit=limit)
        logging.info(f"Starting engine for {len(images)} files (engine={self.ocr_engine})")

        if not images:
            return []

        if incremental:
            filtered_images = []
            for p in images:
                key = os.path.basename(p)
                try:
                    mtime = os.path.getmtime(p)
                except Exception:
                    mtime = None
                prev = self.processed_index.get(key)
                if prev and prev.get("mtime") == mtime:
                    continue
                filtered_images.append(p)
            images = filtered_images
            logging.info(f"Incremental mode: {len(images)} new files to process")
            if not images:
                return []

        workers = self.max_workers if self.max_workers else min(8, max(1, (os.cpu_count() or 4) - 1))
        path_by_filename = {os.path.basename(p): p for p in images}
        total = len(images)
        done = 0
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    self._run_with_timeout,
                    lambda p=path: self.process_document(p),
                    self.ocr_timeout_seconds + 10,
                ): path
                for path in images
            }
            for future in concurrent.futures.as_completed(future_map):
                path = future_map[future]
                try:
                    result = future.result()
                except TimeoutError:
                    logging.warning(
                        f"Timeout processing {os.path.basename(path)} after {self.ocr_timeout_seconds + 10}s"
                    )
                    result = None
                except Exception:
                    logging.exception(f"Unhandled worker failure for {os.path.basename(path)}")
                    result = None

                if result:
                    results.append(result)

                done += 1
                if progress_callback:
                    try:
                        progress_callback(done, total, os.path.basename(path))
                    except Exception:
                        logging.exception("Progress callback failed")

        final_results = [r for r in results if r]

        for r in final_results:
            key = r.get("filename")
            source_path = path_by_filename.get(key)
            if not source_path:
                continue
            try:
                self.processed_index[key] = {
                    "mtime": os.path.getmtime(source_path),
                    "last_processed": datetime.now().isoformat(),
                }
            except Exception:
                self.processed_index[key] = {
                    "mtime": None,
                    "last_processed": datetime.now().isoformat(),
                }

        self._save_processed_index()

        if write_report:
            self.save_results(final_results, output_path=report_path)
        return final_results

    def save_results(self, results, output_path="D:/Agentic_OCR/master_report.csv"):
        if not results:
            return
        keys = results[0].keys()
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            logging.info(f"Report saved to {output_path}")
        except Exception:
            logging.exception("Failed to write report")

    def organize_files(self, results):
        base_dir = "D:/Agentic_OCR/organized_receipts"
        os.makedirs(f"{base_dir}/Verified", exist_ok=True)
        os.makedirs(f"{base_dir}/Needs_Review", exist_ok=True)

        img_source_dir = "D:/Agentic_OCR/data/sroie/SROIE2019/test/img"

        count = 0
        for r in results:
            old_path = os.path.join(img_source_dir, r["filename"])
            category = "Verified" if "VERIFIED" in r["status"] else "Needs_Review"
            new_path = os.path.join(base_dir, category, r["new_name"])

            if os.path.exists(old_path) and not os.path.exists(new_path):
                try:
                    shutil.copy2(old_path, new_path)
                    count += 1
                except Exception:
                    logging.exception(f"Failed to copy {old_path} -> {new_path}")

        logging.info(f"LIBRARIAN: {count} files sorted into {base_dir}")


if __name__ == "__main__":
    agent = ReceiptAgent()
    processed_data = agent.bulk_process("D:/Agentic_OCR/data/sroie", limit=2)
    agent.organize_files(processed_data)
