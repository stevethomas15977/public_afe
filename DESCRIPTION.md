Awesome challenge. Below is a practical, end-to-end Python approach to automatically read a P\&ID’s **margin grid labels** (letters/numbers around the border) and turn them into a usable grid index (e.g., A–H × 1–12). The pipeline is model-light (OpenCV + Tesseract) but extensible to ML when you want to harden it for production.

Why this matters: P\&IDs are the control-layer schematics for plants; they’re widely standardized (e.g., ISA S5.1 for instrumentation tags) and used downstream for HAZOP, operations, etc. Digitizing them reliably—starting with their page grid—accelerates search and cross-references (like “line continues at B-7”). ([Wikipedia][1])

Design notes baked in:

* Many engineering drawings use **zoned borders** with letters on one axis and numbers on the other; some conventions **skip I and O** to avoid confusion with 1 and 0. We lean on that to validate/clean OCR. ([The CAD Setter Out][2])
* We focus on **margin capture** (thin strips at each edge) rather than the whole sheet, which improves OCR signal-to-noise on busy P\&IDs. Technique: border detection → crop edge bands → binarize → OCR → sequence validation.
* We’ll infer cell boundaries from the **count and order** of labels. If you read 8 letters vertically and 12 numbers horizontally, we divide the drawable area into an 8×12 lattice.
* Implementation uses OpenCV + Tesseract (battle-tested combo for engineered docs), with easy hooks to add deep models later (e.g., DB/CRAFT for text detection). ([PyImageSearch][3])

---

# Python: P\&ID Grid Label Parser (letters/numbers on margins)

```python
"""
pid_grid_parser.py

Reads a scanned/digital P&ID (PNG/JPG/PDF), detects page border, OCRs the grid labels
around the margins, validates their sequences (letters vs numbers), and returns:
- rows: ordered list of row labels (e.g., ["A","B","C",...])
- cols: ordered list of column labels (e.g., ["1","2","3",...])
- layout: pixel-to-grid mapping helpers so you can convert (x,y) -> ("B", "7")

Deps:
  pip install opencv-python pytesseract pdf2image pillow numpy
System:
  - Install Tesseract OCR (e.g., apt-get install tesseract-ocr)
"""

import os
import cv2
import numpy as np
import pytesseract
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

# ---- Config knobs ------------------------------------------------------------

# Margin band widths (in pixels) relative to the smallest image dimension.
# Adjust if your scans have wider/narrower borders.
TOP_BAND_FRAC    = 0.07
BOTTOM_BAND_FRAC = 0.07
LEFT_BAND_FRAC   = 0.07
RIGHT_BAND_FRAC  = 0.07

# Minimum/maximum number of expected grid labels. Tune to your standards.
MIN_LABELS_PER_AXIS = 3
MAX_LABELS_PER_AXIS = 50

# Whether to skip I and O in the letter sequence (common drafting practice).
SKIP_AMBIG_LETTERS = True  # I and O skipped to avoid confusion with 1 and 0.

# Tesseract OCR config tuned for single-line, high-contrast text
TESS_CONFIG = r"--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

# ---- Helpers ----------------------------------------------------------------

def load_image(path: str, dpi: int = 300) -> np.ndarray:
    """Load image or first page of a PDF as BGR numpy array."""
    ext = os.path.splitext(path.lower())[1]
    if ext == ".pdf":
        if convert_from_path is None:
            raise RuntimeError("pdf2image not installed. pip install pdf2image and poppler.")
        pages = convert_from_path(path, dpi=dpi)
        if not pages:
            raise ValueError("PDF has no pages.")
        img = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)
        return img
    else:
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Could not read image: {path}")
        return img

def detect_page_rect(img: np.ndarray) -> Tuple[int,int,int,int]:
    """
    Rough page border detection:
    - convert to gray, blur, Canny
    - find the largest contour with near-rect shape
    - return (x,y,w,h) bounding box
    Fallback: If fail, return the whole image bounds.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)

    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        h, w = img.shape[:2]
        return 0, 0, w, h

    # largest contour by area
    c = max(cnts, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)

    # sanity: ensure it covers big portion; else return whole frame
    H, W = img.shape[:2]
    if w*h < 0.5*W*H:
        return 0, 0, W, H
    return x, y, w, h

def crop_margin_bands(img: np.ndarray, page_rect: Tuple[int,int,int,int]):
    x, y, w, h = page_rect
    page = img[y:y+h, x:x+w]
    H, W = page.shape[:2]

    top    = page[0:int(TOP_BAND_FRAC*H), :]
    bottom = page[int((1-BOTTOM_BAND_FRAC)*H):, :]
    left   = page[:, 0:int(LEFT_BAND_FRAC*W)]
    right  = page[:, int((1-RIGHT_BAND_FRAC)*W):]
    return page, top, bottom, left, right

def prep_for_ocr(img: np.ndarray) -> np.ndarray:
    """High-contrast binarization to help OCR."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Adaptive threshold handles uneven lighting on scans
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 35, 15)
    # Optional: morphological open to reduce fine lines
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    return bw

def ocr_text_line(img: np.ndarray) -> str:
    """Run Tesseract on a (mostly) single text line region."""
    bw = prep_for_ocr(img)
    txt = pytesseract.image_to_string(bw, config=TESS_CONFIG)
    return txt.strip()

def extract_tokens_along_axis(strip_img: np.ndarray, axis: str) -> List[Tuple[str, Tuple[int,int,int,int]]]:
    """
    Given a top/bottom (axis='x') or left/right (axis='y') strip, find text blobs
    and OCR each one. Return [(token, bbox), ...] in reading order.
    """
    gray = cv2.cvtColor(strip_img, cv2.COLOR_BGR2GRAY)
    bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    # Invert if text is white (heuristic)
    if np.mean(bw) > 127:
        bw = 255 - bw

    # Find connected components as candidate tokens
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w*h < 50:  # skip tiny noise
            continue
        boxes.append((x, y, w, h))

    # Sort reading order
    if axis == 'x':  # left->right for top/bottom
        boxes.sort(key=lambda b: b[0])
    else:            # top->bottom for left/right
        boxes.sort(key=lambda b: b[1])

    tokens = []
    for (x, y, w, h) in boxes:
        roi = strip_img[y:y+h, x:x+w]
        t = ocr_text_line(roi)
        if t:
            # keep only alnum + hyphen (some drawings use 10-20 etc.)
            t_clean = ''.join(ch for ch in t if ch.isalnum() or ch == '-')
            if t_clean:
                tokens.append((t_clean, (x, y, w, h)))
    return tokens

def normalize_letter_sequence(seq: List[str]) -> List[str]:
    """Uppercase, remove non-letters, collapse duplicates, optionally skip I/O."""
    out = []
    for s in seq:
        s = ''.join([c for c in s.upper() if c.isalpha()])
        if not s:
            continue
        out.append(s)
    # De-dup consecutive duplicates caused by split bounding boxes
    dedup = []
    for s in out:
        if not dedup or dedup[-1] != s:
            dedup.append(s)

    if SKIP_AMBIG_LETTERS:
        dedup = [s for s in dedup if s not in ('I','O')]
    return dedup

def normalize_number_sequence(seq: List[str]) -> List[str]:
    """Keep integers (possibly hyphenated like 10-20, split if necessary)."""
    out = []
    for s in seq:
        s = s.replace('O', '0')  # common OCR confusion
        # Handle ranges like 10-20 (rare for zone labels; still split)
        parts = [p for chunk in s.split('-') for p in chunk.split()]
        for p in parts:
            if p.isdigit():
                out.append(str(int(p)))  # normalize leading zeros
    # De-dup consecutive duplicates
    dedup = []
    for s in out:
        if not dedup or dedup[-1] != s:
            dedup.append(s)
    return dedup

def choose_axis_labels(top_tokens, bottom_tokens, left_tokens, right_tokens):
    """
    Decide which axis is letters vs numbers.
    Heuristics:
      - The axis where tokens are predominantly letters => row labels
      - The axis where tokens are mostly numbers => column labels
      - Merge top+bottom for X; left+right for Y; prefer the longer/cleaner list.
    """
    top_seq    = [t for t,_ in top_tokens]
    bottom_seq = [t for t,_ in bottom_tokens]
    left_seq   = [t for t,_ in left_tokens]
    right_seq  = [t for t,_ in right_tokens]

    x_seq_raw = top_seq if len(top_seq) >= len(bottom_seq) else bottom_seq
    y_seq_raw = left_seq if len(left_seq) >= len(right_seq) else right_seq

    x_letters = normalize_letter_sequence(x_seq_raw)
    x_numbers = normalize_number_sequence(x_seq_raw)
    y_letters = normalize_letter_sequence(y_seq_raw)
    y_numbers = normalize_number_sequence(y_seq_raw)

    # Prefer convention: letters on vertical axis, numbers on horizontal
    # but support flipped drawings.
    # Case 1: y has letters and x has numbers -> rows=y letters, cols=x numbers
    if len(y_letters) >= MIN_LABELS_PER_AXIS and len(x_numbers) >= MIN_LABELS_PER_AXIS:
        return y_letters, x_numbers, 'letters-on-y'
    # Case 2: x has letters and y has numbers -> rows=x letters, cols=y numbers
    if len(x_letters) >= MIN_LABELS_PER_AXIS and len(y_numbers) >= MIN_LABELS_PER_AXIS:
        return x_letters, y_numbers, 'letters-on-x'
    # Fallback: pick whichever looks more plausible by length
    # (works even if both axes are numbers or both letters, uncommon)
    candidates = [
        ('xL_yN', x_letters, y_numbers),
        ('yL_xN', y_letters, x_numbers)
    ]
    candidates.sort(key=lambda r: (len(r[1]) >= MIN_LABELS_PER_AXIS) + (len(r[2]) >= MIN_LABELS_PER_AXIS), reverse=True)
    tag, a, b = candidates[0]
    return (a, b, tag)

@dataclass
class GridLayout:
    rows: List[str]
    cols: List[str]
    page_rect: Tuple[int,int,int,int]
    row_bands: List[Tuple[int,int]]  # y pixel ranges within page (top->bottom)
    col_bands: List[Tuple[int,int]]  # x pixel ranges within page (left->right)]

    def locate(self, x: int, y: int) -> Tuple[Optional[str], Optional[str]]:
        """Convert a page-relative (x,y) into (row_label, col_label)."""
        rx = ry = None
        for i,(x0,x1) in enumerate(self.col_bands):
            if x0 <= x < x1:
                rx = self.cols[i]
                break
        for j,(y0,y1) in enumerate(self.row_bands):
            if y0 <= y < y1:
                ry = self.rows[j]
                break
        # Return (row, col) in conventional order like ("B","7")
        return (ry, rx)

def build_bands(page_wh: Tuple[int,int], n_rows: int, n_cols: int) -> Tuple[List[Tuple[int,int]], List[Tuple[int,int]]]:
    """Uniform bands across the drawable page rect."""
    W, H = page_wh
    col_edges = np.linspace(0, W, n_cols+1).astype(int)
    row_edges = np.linspace(0, H, n_rows+1).astype(int)
    col_bands = [(col_edges[i], col_edges[i+1]) for i in range(n_cols)]
    row_bands = [(row_edges[i], row_edges[i+1]) for i in range(n_rows)]
    return row_bands, col_bands

def parse_pid_grid(image_path: str) -> GridLayout:
    img = load_image(image_path)
    px, py, pw, ph = detect_page_rect(img)
    page, top, bottom, left, right = crop_margin_bands(img, (px,py,pw,ph))

    # Extract tokens from each margin
    top_toks    = extract_tokens_along_axis(top, axis='x')
    bottom_toks = extract_tokens_along_axis(bottom, axis='x')
    left_toks   = extract_tokens_along_axis(left, axis='y')
    right_toks  = extract_tokens_along_axis(right, axis='y')

    rows, cols, mode = choose_axis_labels(top_toks, bottom_toks, left_toks, right_toks)

    if not (MIN_LABELS_PER_AXIS <= len(rows) <= MAX_LABELS_PER_AXIS):
        raise ValueError(f"Row labels unreliable: {rows}")
    if not (MIN_LABELS_PER_AXIS <= len(cols) <= MAX_LABELS_PER_AXIS):
        raise ValueError(f"Column labels unreliable: {cols}")

    # Build grid bands across page area
    row_bands, col_bands = build_bands((pw, ph), len(rows), len(cols))

    return GridLayout(
        rows=rows,
        cols=cols,
        page_rect=(px,py,pw,ph),
        row_bands=row_bands,
        col_bands=col_bands
    )

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pid_grid_parser.py <image_or_pdf_path>")
        sys.exit(1)

    layout = parse_pid_grid(sys.argv[1])
    out = {
        "rows": layout.rows,
        "cols": layout.cols,
        "page_rect": layout.page_rect,
        "row_bands": layout.row_bands,
        "col_bands": layout.col_bands
    }
    print(json.dumps(out, indent=2))
```

## How it works (quick tour)

1. **Load** the image/PDF’s first page.
2. **Detect page border** by finding the largest outer contour (robust to scanner margins).
3. **Crop four margin strips** (top/bottom/left/right).
4. **Detect & OCR tokens** in each strip (connected components → small crops → Tesseract with a whitelist). OpenCV+Tesseract is a well-established baseline for OCR pipelines and can be upgraded with deep text detectors if needed. ([PyImageSearch][3])
5. **Validate sequences**: letters vs numbers, de-duplicate, optionally **skip I/O** (common drafting practice). ([The CAD Setter Out][2])
6. **Infer lattice** size from counts → create uniform **row/column bands** across the drawable page rectangle.
7. Provide a `locate(x,y)` helper to map any coordinate to grid (e.g., (“B”, “7”)).

---

## Tuning & production hardening

* **When labels are rotated** (e.g., left/right are rotated 90°), Tesseract usually handles them if ROI is upright. If not, auto-rotate those ROIs by ±90° and re-OCR.
* **Non-uniform spacing**: Some drawings have unequal zones (e.g., larger title-block edge). Detect internal **gridlines** with Hough Line Transform, then align band edges to peaks instead of uniform spacing. (Start simple; add line-based snapping as needed.)
* **Better text detection**: Swap CC-based box finding with a DL text detector (e.g., DB/CRAFT) when you hit noisy prints and dense borders. Keep Tesseract (or a lightweight CRNN) for recognition. ([iTech India][4])
* **Standards awareness**: Many engineering drawings follow ASME Y14 family (formatting/zoning). If your clients adhere to it, bake the expected zone counts, letter skipping, and title-block offsets into validation rules. ([ASME][5])
* **P\&ID context**: If you later glue this to tag extraction (ISA S5.1), you can cross-index equipment/line continuations with grid references in your database/UI. ([Wikipedia][1])

---

## Usage examples

```bash
# image
python pid_grid_parser.py /path/to/pid_scan.png

# pdf (needs poppler for pdf2image)
python pid_grid_parser.py /path/to/pid_drawing.pdf
```

The JSON output gives you `rows`, `cols`, and the pixel bands. To tag an OCR-detected item or a click in a web viewer, convert the click’s page-relative (x,y) with `GridLayout.locate()`.

---

## Why these choices (and sources)

* **P\&ID role & standard symbols**: Definitions and ISA S5.1 context come from Wikipedia’s overview (good general reference). ([Wikipedia][1])
* **Grid conventions** (letters vertically, numbers horizontally, skip I and O) are long-standing drafting practices; we use them as post-OCR priors. ([The CAD Setter Out][2])
* **OCR pipeline**: OpenCV pre-processing + Tesseract is a proven starting point, with tutorials and patterns you can adapt for engineered documents and even MRZ-like structured zones. ([PyImageSearch][3])
* **Industrial OCR on drawings**: Contemporary guides outline challenges and ML add-ons (DB/CRAFT detectors, contour-based ROIing), which you can adopt as accuracy demands rise. ([iTech India][4])

If you want, I can add an optional Hough-line snap step (to align the bands to detected gridlines) and a tiny CLI flag to export a **GeoJSON-like** layer of grid cells for web viewers.

[1]: https://en.wikipedia.org/wiki/Piping_and_instrumentation_diagram?utm_source=chatgpt.com "Piping and instrumentation diagram"
[2]: https://cadsetterout.com/drawing-standards/grid-reference-frame/?utm_source=chatgpt.com "Technical Drawing Standards: Grid Reference Frame."
[3]: https://pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/?utm_source=chatgpt.com "OpenCV OCR and text recognition with Tesseract"
[4]: https://itechindia.co/us/blog/guide-to-ocr-technology-for-engineering-drawings/?utm_source=chatgpt.com "Guide to AI-based OCR for Engineering Drawings and ..."
[5]: https://www.asme.org/codes-standards/y14-standards?utm_source=chatgpt.com "ASME's Y14 Standard"
