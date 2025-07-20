from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Competitor, AnalysisResult, Conversation
from app.learning_agent import LearningAgent

load_dotenv()

from app.database import init_db

app = Flask(__name__)
db = SessionLocal()
agent = LearningAgent() # We can share one agent instance

@app.before_request
def create_tables_if_not_exist():
    # This function will run before the first request to the application.
    # It's a robust way to ensure the database is ready.
    init_db()

@app.route("/")
def dashboard():
    """
    Renders the main dashboard page.
    """
    competitors = db.query(Competitor).all()
    latest_analyses = db.query(AnalysisResult).order_by(AnalysisResult.analysis_date.desc()).limit(5).all()
    return render_template("dashboard.html", competitors=competitors, analyses=latest_analyses)

from sqlalchemy.orm import joinedload

@app.route("/competitors")
def competitors_page():
    """
    Renders the page showing all competitors and their analyses.
    """
    all_competitors = db.query(Competitor).options(
        joinedload(Competitor.analysis_results)
    ).all()
    return render_template("competitors.html", competitors=all_competitors)

@app.route("/chat")
def chat_page():
    """
    Renders the chat interface page.
    """
    history = agent._load_history() # Using the agent's method to get current session history
    return render_template("chat.html", history=history)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    API endpoint to handle chat messages from the web interface.
    It can now handle both text and image uploads.
    """
    if 'message' not in request.form:
        return jsonify({"error": "No message provided"}), 400

    user_message = request.form.get("message")
    ai_response = ""

    if 'image' in request.files and request.files['image'].filename != '':
        image_file = request.files['image']
        # Save the file temporarily to pass its path to the agent
        # A more robust solution might use a temporary directory
        temp_path = os.path.join("temp_uploads", image_file.filename)
        os.makedirs("temp_uploads", exist_ok=True)
        image_file.save(temp_path)

        # Use the multimodal model for analysis
        # Ensure you have a model like 'llava' pulled in Ollama
        ai_response = agent.analyze_image(user_message, temp_path, model="llava")

        # Clean up the temporary file
        os.remove(temp_path)
    else:
        # Standard text-only chat
        ai_response = agent.chat(user_message)

    return jsonify({"response": ai_response})

if __name__ == "__main__":
    # Make sure to create the database first by running:
    # python -m app.database
    app.run(debug=True, host='0.0.0.0', port=5000)
