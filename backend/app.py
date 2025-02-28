from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  #Load environment variables from .env

app = Flask(__name__)

@app.route('/')
def home():
    return f"BackEnd is running! {os.getenv('FLASK_ENV')}  mode!"

if __name__ == '__main__':
    app.run(debug=True)

