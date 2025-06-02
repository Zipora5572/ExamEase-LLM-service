from flask import Flask
from flask_cors import CORS
from routes import register_routes
import os
from dotenv import load_dotenv

load_dotenv()  # טוען משתני סביבה מקובץ .env

FLASK_ENV = os.getenv("FLASK_ENV", "production")  # ברירת מחדל production

debug_mode = FLASK_ENV == "development"

app = Flask(__name__)
app.config['DEBUG'] = debug_mode
CORS(app)

# רישום הראוטים
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
