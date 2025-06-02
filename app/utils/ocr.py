import pytesseract
from PIL import Image

def image_to_text(image, lang='eng+heb'):
    lang = 'eng' if 'eng' in lang else 'heb' if 'heb' in lang else 'eng+heb'
    print(lang)
    return pytesseract.image_to_string(image, lang=lang)
