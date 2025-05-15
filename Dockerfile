# בסיס של פייתון
FROM python:3.12-slim

# התקנת תלות למנוע Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/


# הגדרת תקיית העבודה
WORKDIR /app

# העתקת הקבצים לקונטיינר
COPY . /app

# התקנת התלויות
RUN pip install --no-cache-dir -r requirements.txt

# חשיפת הפורט החדש
EXPOSE 5000

# הרצת האפליקציה
CMD ["python", "main.py"]
