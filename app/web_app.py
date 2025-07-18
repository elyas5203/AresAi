from flask import Flask, render_template, request, jsonify
from app.database import SessionLocal
from app.models import Competitor, AnalysisResult, Conversation
from app.learning_agent import LearningAgent

app = Flask(__name__)
db = SessionLocal()
agent = LearningAgent() # We can share one agent instance

@app.route("/")
def dashboard():
    """
    Renders the main dashboard page.
    """
    competitors = db.query(Competitor).all()
    latest_analyses = db.query(AnalysisResult).order_by(AnalysisResult.analysis_date.desc()).limit(5).all()
    return render_template("dashboard.html", competitors=competitors, analyses=latest_analyses)

@app.route("/competitors")
def competitors_page():
    """
    Renders the page showing all competitors and their analyses.
    """
    all_competitors = db.query(Competitor).options(
        db.joinedload(Competitor.analysis_results)
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
    """
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    ai_response = agent.chat(user_message)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    # Make sure to create the database first by running:
    # python -m app.database
    app.run(debug=True)
