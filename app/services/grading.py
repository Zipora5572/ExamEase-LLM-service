from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
my_model = "gpt-4o-mini"

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
