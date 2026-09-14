import os
import logging
from abc import ABC, abstractmethod
from typing import List

log = logging.getLogger("screenshot.ocr")


class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> List[str]:
        pass


class PaddleOCRProvider(OCRProvider):
    def __init__(self):
        self._ocr = None

    def _load(self):
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR

                self._ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
                log.info("PaddleOCR loaded")
            except Exception as e:
                log.debug(f"PaddleOCR not available: {e}")
                self._ocr = False
        return self._ocr

    def extract_text(self, image_bytes: bytes) -> List[str]:
        ocr = self._load()
        if not ocr:
            return fallback_extract(image_bytes)
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(image_bytes)
                p = f.name
            result = ocr.ocr(p, cls=True)
            os.unlink(p)
            lines = []
            if result and result[0]:
                for line in result[0]:
                    txt = (
                        line[1][0]
                        if isinstance(line[1], (list, tuple))
                        else str(line[1])
                    )
                    if txt.strip():
                        lines.append(txt.strip())
            if lines:
                log.info(f"PaddleOCR extracted {len(lines)} lines")
                return lines
            return fallback_extract(image_bytes)
        except Exception as e:
            log.warning(f"PaddleOCR failed: {e}")
            return fallback_extract(image_bytes)


def _enhance_for_tesseract(image_bytes: bytes):
    from PIL import Image, ImageOps, ImageEnhance
    import io

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "L":
        img = img.convert("L")
    w, h = img.size
    if w < 900:
        scale = 900 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.6)
    try:
        img = img.point(lambda x: 0 if x < 140 else 255, "L")
    except:
        pass
    return img


def fallback_extract(image_bytes: bytes) -> List[str]:
    try:
        import pytesseract

        cmd = os.getenv("TESSERACT_CMD", "").strip().strip('"').strip("'").strip()
        if cmd:
            pytesseract.pytesseract.tesseract_cmd = cmd
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            log.warning(
                f"Tesseract binary missing: {e} — using vision fallback (set TESSERACT_CMD or add to PATH)"
            )
            return vision_fallback(image_bytes)
        img = _enhance_for_tesseract(image_bytes)
        configs = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 3",
            "--oem 1 --psm 6 -c preserve_interword_spaces=1",
        ]
        for cfg in configs:
            try:
                text = pytesseract.image_to_string(img, config=cfg)
                lines = [
                    l.strip()
                    for l in text.splitlines()
                    if l.strip() and len(l.strip()) > 1
                ]
                if lines:
                    log.info(f"pytesseract extracted {len(lines)} lines with {cfg}")
                    return lines
            except:
                continue
        return []
    except Exception as e:
        log.warning(f"fallback_extract failed: {e}")
        return vision_fallback(image_bytes)


def vision_fallback(image_bytes: bytes) -> List[str]:
    return []


_provider: OCRProvider = PaddleOCRProvider()


def get_ocr_provider() -> OCRProvider:
    return _provider


def extract_lines(image_bytes: bytes) -> List[str]:
    lines = get_ocr_provider().extract_text(image_bytes)
    log.debug(f"extract_lines -> {len(lines)} lines")
    return lines
