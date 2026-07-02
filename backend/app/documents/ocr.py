from __future__ import annotations
from pathlib import Path


def ocr_image(path: str | Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        import cv2
        import pytesseract
        img = cv2.imread(str(path))
        if img is None:
            return "", ["Image could not be decoded"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(gray)
        if not text.strip():
            warnings.append("OCR returned empty text")
        return text.strip(), warnings
    except Exception as exc:
        return "", [f"OCR fallback unavailable or failed: {exc}"]
