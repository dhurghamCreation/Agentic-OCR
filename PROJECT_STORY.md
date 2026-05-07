Project Highlight: Solving OCR Inaccuracies via Heuristics

While processing a complex receipt (Lightroom Gallery), the OCR engine (RapidOCR) misread the 'TOTAL' label as 'TOT''. This caused traditional keyword-matching scripts to fail.

My Solution: I implemented a Maximum Value Heuristic. By programmatically extracting all numerical candidates that fit a currency profile (0.00) and selecting the maximum value within a standard deviation, the Agent successfully extracted the correct Grand Total of 278.80, bypassing the OCR typo entirely. This increased the pipeline's robustness against non-standard document formatting.