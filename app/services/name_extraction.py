from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
my_model = "gpt-4o-mini"

def extract_name_from_text_using_list(student_text, student_list):
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
        result = json.loads(response.choices[0].message.content)
        firstName = result.get("firstName")
        lastName = result.get("lastName")
        confidence = int(result.get("confidence", 0))
        if firstName != "Null" and lastName != "Null":
            return firstName, lastName, confidence
    except Exception as e:
        print("AI name extract error:", e)

    return "Null", "Null", 0
