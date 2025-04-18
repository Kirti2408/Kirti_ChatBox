from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from pathlib import Path
import os

# LangChain Imports
from langchain_community.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Error: OPENAI_API_KEY not found in .env file")

# Initialize LangChain LLM and memory
llm = OpenAI(openai_api_key=openai_api_key)
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Secret key for session and flash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/lawyer')
def ask_lawyer():
    return render_template('ask_lawyer.html')

@app.route('/contact', methods=["GET", "POST"])
def contact():
    return render_template('contact.html')

@app.route('/indexai')
def indexai():
    return render_template('indexai.html')

# User Registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# User Login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_name'] = user.name
            flash("You have logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')


# Optional: Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# LangChain Chat API
@app.route('/data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        user_input = data.get('data', '')

        if not user_input:
            return jsonify({"response": False, "message": "No input received."})

        conversation = ConversationChain(llm=llm, memory=memory, verbose=True)
        output = conversation.predict(input=user_input)

        memory.save_context({"input": user_input}, {"output": output})

        return jsonify({"response": True, "message": output})

    except Exception as e:
        return jsonify({"response": False, "message": f"Error: {str(e)}"})

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
