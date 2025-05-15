import pytesseract
from PIL import Image

def image_to_text(image, lang='eng+heb'):
    return pytesseract.image_to_string(image, lang=lang)
