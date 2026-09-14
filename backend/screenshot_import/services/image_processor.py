from PIL import Image
import io

MAX_SIZE = 5 * 1024 * 1024
ALLOWED = {"image/jpeg", "image/png", "image/webp"}
MAX_DIM = 2048


def validate_image(file):
    if file.size > MAX_SIZE:
        raise ValueError("Max 5MB")
    ct = getattr(file, "content_type", None)
    name = getattr(file, "name", "") or ""
    if ct:
        ct = ct.lower()
        if ct == "image/jpg":
            ct = "image/jpeg"
        if ct not in ALLOWED:
            raise ValueError(f"Only JPEG/PNG/WebP (got {ct})")
    elif name:
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in ("jpg", "jpeg", "png", "webp"):
            raise ValueError("Only JPEG/PNG/WebP")
    return True


def _is_dark(img):
    try:
        from PIL import ImageStat

        gray = img.convert("L")
        stat = ImageStat.Stat(gray)
        return stat.mean[0] < 100
    except:
        return False


def preprocess(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    if _is_dark(img):
        from PIL import ImageOps

        img = ImageOps.invert(img)
    w, h = img.size
    if max(w, h) > MAX_DIM:
        ratio = MAX_DIM / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=92)
    return out.getvalue()
