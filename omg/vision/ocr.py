try:
    import pytesseract
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract"])
    import pytesseract
except Exception:
    pytesseract = None
from PIL import Image
import logging
import os

class OCRAngine:
    def __init__(self):
        self.available = pytesseract is not None
        if self.available:
            # Common Windows Tesseract Paths
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Users\\' + os.getlogin() + r'\AppData\Local\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logging.info(f"✅ Tesseract Binary Found at: {path}")
                    break
        else:
            logging.error("OCR Error: pytesseract Python module not found.")
        pass

    def extract_text_with_positions(self, image: Image.Image):
        """
        Returns a list of dicts: [{'text': 'Next', 'x': 100, 'y': 200, 'w': 50, 'h': 20, 'center': (125, 210)}, ...]
        """
        if not self.available:
            return []
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            results = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    results.append({
                        'text': text,
                        'x': x,
                        'y': y,
                        'w': w,
                        'h': h,
                        'center': (x + w // 2, y + h // 2)
                    })
            return results
        except Exception as e:
            logging.error(f"OCR Error: {e}")
            return []

    def find_text_coordinates(self, target_text, ocr_results):
        """
        Finds the coordinates of the target_text in the ocr_results.
        Supports fuzzy matching or exact matching.
        """
        target_text = target_text.lower()
        for res in ocr_results:
            if target_text in res['text'].lower():
                return res['center']
        
        # Try joining close results if needed? For now simple matching.
        return None
