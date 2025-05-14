import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.cloud import storage
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
from openai import OpenAI
import requests
import json
import base64


app = Flask(__name__)
CORS(app)
SERVICE_ACCOUNT_FILE = "./client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = my_api_key

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
client = OpenAI()
my_model = "gpt-4o-mini"
def extract_name_from_text_using_list(student_text, student_list):
    print(student_list)
    names_str = "\n".join(student_list)
    prompt = f"""
    להלן רשימת שמות של תלמידות:
    {names_str}

    זהו טקסט שנלקח ממבחן של אחת מהן:
    {student_text}

    הוראות חשובות:
    - עליך לבחור אך ורק שם מתוך הרשימה – אסור להמציא שמות שלא קיימים בה.
    - גם אם מופיע בטקסט שם דומה אך שגוי בכתיב, עליך להתאים אותו לשם הכי דומה מהרשימה **ולהחזיר את הניסוח המדויק שמופיע ברשימה**.
    - אם אין התאמה סבירה – החזר "Null".

    📌 הפלט חייב להיות בקובץ JSON בלבד, ללא הסברים, וללא טקסט נוסף, ובפורמט הבא:
    הפלט חייב להתחיל בסוגריים המסולסלות של ה JSON
    {{
    "firstName": "שם פרטי מתוך הרשימה או Null",
    "lastName": "שם משפחה מתוך הרשימה או Null",
    "confidence": "אחוזים מ-0 עד 100"
    }}
    """

    response = client.chat.completions.create(
        model=my_model,
        messages=[
            {"role": "system", "content": "אתה מזהה שמות של תלמידות מתוך טקסטים של מבחנים."},
            {"role": "user", "content": prompt}
        ]
    )
   
    try:
        # print(response.choices)
        result = json.loads(response.choices[0].message.content)
        print(result)
        firstName = result.get("firstName")
        lastName = result.get("lastName")
        confidence = int(result.get("confidence", 0))
        if firstName != "Null" and lastName != "Null":
            return firstName,lastName, confidence
    except Exception as e:
        print("AI name extract error:", e)

    return "Null", "Null", 0


def grade_exam(student_exam, teacher_exam):
    print(student_exam)
    print(teacher_exam)
    prompt = f"""
    תלמידה ענתה על המבחן הבא:
    {student_exam}

    התשובות הנכונות הן:
    {teacher_exam}

    אנא תן ציון מדויק באחוזים לתשובות של התלמידה והסבר את הציון. אם התשובות של התלמידה נכונות, גם אם הן שונות מהתשובות של המורה, אנא ציין זאת כ"נכון",  והסבר שהן כוללות את המידע הבסיסי הנדרש. 
    אם התשובות נכונות אך חסרות פרטים זניחים , יש לציין זאת, אך לא להוריד ציונים  .
    אם יש בהן חלק שגוי לחלוטין אז יש להוריד 
     החזר את התשובות בפורמט JSON כך:
     ללא הוספת המילה JSON 
     התשובה צריכה להתחיל ישר ב 
    {{
        "grade": "ציון באחוזים",
        "evaluation": "הערכה במילים"
    }}
    """
    
    response = client.chat.completions.create(
        model=my_model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
   
    
    return response.choices[0].message.content

    try:
        url = "http://localhost:5001/recognize"
        files = {'image': image_stream}
        response = requests.post(url, files=files)
        response.raise_for_status() 
        result = response.json()
        return result.get("text", "")
    except Exception as e:
        print(f"Error recognizing text: {e}")
        raise 
    

@app.route('/grade', methods=['OPTIONS'])
def options():
    return jsonify({'status': 'ok'}), 200




    
#     data = request.json
#     student_exam_name = data.get('student_exam_name')
#     student_names_list = data.get('student_names_list')

#     if not student_exam_name or not student_names_list:
#         return jsonify({"error": "Missing student_exam_name or student_names_list"}), 400

#     try:
        
#         student_exam_image = download_blob("exams-bucket", student_exam_name)
        
#         student_image = Image.open(student_exam_image)
#         student_exam_text = pytesseract.image_to_string(student_image)

#         print(student_exam_text)
#         firstName,lastName, confidence = extract_name_from_text_using_list(student_exam_text, student_names_list)
        

#         return jsonify({
#             "firstName": firstName,
#             "lastName": lastName,
#             "confidence": confidence,
#         })

#     except Exception as e:
#         print(e)
#         return jsonify({"error": str(e)}), 500
@app.route('/extract-name', methods=['POST'])
def extract_name():
    print("HEADERS:", request.headers)
    print("CONTENT TYPE:", request.content_type)

    uploaded_file = request.files.get('file')
  
    student_names_list = request.form.get('student_names_list')
    print("student_names_list: ", student_names_list)
    language = request.form.get('language', 'eng+heb') 

    if not uploaded_file or not student_names_list:
        return jsonify({"error": "Missing file or student_names_list"}), 400

    try:
        student_names_list = json.loads(student_names_list)  
        student_image = Image.open(uploaded_file)
        student_exam_text = pytesseract.image_to_string(student_image, lang=language)
        print("list: ",student_names_list)

        firstName, lastName, confidence = extract_name_from_text_using_list(student_exam_text, student_names_list)

        return jsonify({
            "firstName": firstName,
            "lastName": lastName,
            "confidence": confidence,
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/detect-language', methods=['POST'])
def detect_language():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Missing file"}), 400

        file = request.files.get('file')
        image = Image.open(file)
       
        text = pytesseract.image_to_string(image, lang='eng+heb')

        if not text.strip():
            return jsonify({"language": "unknown"})

        lang_code = detect(text)

        if lang_code == 'he':
            language = 'heb'
        elif lang_code == 'en':
            language = 'eng'
        else:
            language = 'unknown'

        return jsonify({
            "language": language
        })

    except Exception as e:
        return jsonify({"language": "unknown", "error": str(e)}), 500


@app.route('/grade', methods=['POST'])
def grade():
    print(request.headers)
    if 'student_exam' not in request.files or 'teacher_exam' not in request.files:
        return jsonify({"error": "Missing student_exam or teacher_exam file"}), 400

    try:
        student_exam_file = request.files['student_exam']
        teacher_exam_file = request.files['teacher_exam']
        language = request.form.get('lang', 'eng+heb') 

        student_image = Image.open(student_exam_file.stream)
        teacher_image = Image.open(teacher_exam_file.stream)

        student_exam_text = pytesseract.image_to_string(student_image, lang=language)
        teacher_exam_text = pytesseract.image_to_string(teacher_image, lang=language)

        grade_result = grade_exam(student_exam_text, teacher_exam_text)
        result_json = json.loads(grade_result)
        grade = result_json.get("grade")
        evaluation = result_json.get("evaluation")
        print("Grade:", grade)
        print("Evaluation:", evaluation)
        return jsonify({
            "grade": grade,
            "evaluation": evaluation
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
