from flask import request, jsonify
from PIL import Image
import pytesseract
import json
from langdetect import detect
from services.name_extraction import extract_name_from_text_using_list
from services.grading import grade_exam

def register_routes(app):


    @app.route('/')
    def home():
        return 'Hello, World!'


    @app.route('/extract-name', methods=['POST'])
    def extract_name():
        uploaded_file = request.files.get('file')
        student_names_list = request.form.get('student_names_list')
        language = request.form.get('language', 'eng+heb')

        if not uploaded_file or not student_names_list:
            return jsonify({"error": "Missing file or student_names_list"}), 400

        try:
            student_names_list = json.loads(student_names_list)
            student_image = Image.open(uploaded_file)
            student_exam_text = pytesseract.image_to_string(student_image, lang=language)

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
        if 'student_exam' not in request.files or 'teacher_exam' not in request.files:
            return jsonify({"error": "Missing student_exam or teacher_exam file"}), 400

        try:
            student_exam_file = request.files['student_exam']
            teacher_exam_file = request.files['teacher_exam']
            language = request.form.get('lang', 'eng+heb')
            language = 'eng' if 'eng' in language else 'heb' if 'heb' in language else 'eng+heb'

            student_image = Image.open(student_exam_file.stream)
            teacher_image = Image.open(teacher_exam_file.stream)

            student_exam_text = pytesseract.image_to_string(student_image, lang=language)
            teacher_exam_text = pytesseract.image_to_string(teacher_image, lang=language)

            grade_result = grade_exam(student_exam_text, teacher_exam_text)
            result_json = json.loads(grade_result)
            grade = result_json.get("grade")
            evaluation = result_json.get("evaluation")

            return jsonify({
                "grade": grade,
                "evaluation": evaluation
            })

        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500
