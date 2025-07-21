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

@app.route("/competitor-dashboard")
def competitor_dashboard():
    """
    Renders the competitor analysis dashboard with charts.
    """
    all_analyses = db.query(AnalysisResult).options(
        joinedload(AnalysisResult.competitor)
    ).order_by(AnalysisResult.analysis_date.desc()).limit(10).all()
    return render_template("competitor_dashboard.html", analyses=all_analyses)

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

@app.route("/hashtag-suggester", methods=["GET"])
def hashtag_suggester_page():
    """Renders the hashtag suggester page."""
    return render_template("hashtag_suggester.html")

@app.route("/api/suggest-hashtags", methods=["POST"])
def api_suggest_hashtags():
    """
    API endpoint to handle hashtag suggestions.
    """
    if 'caption' not in request.form:
        return jsonify({"error": "No caption provided"}), 400

    caption = request.form.get("caption")
    image_path = None

    if 'image' in request.files and request.files['image'].filename != '':
        image_file = request.files['image']
        temp_path = os.path.join("temp_uploads", image_file.filename)
        os.makedirs("temp_uploads", exist_ok=True)
        image_file.save(temp_path)
        image_path = temp_path

    hashtags = agent.suggest_hashtags(caption, image_path=image_path)

    if image_path:
        os.remove(image_path)

    return jsonify({"hashtags": hashtags})

@app.route("/manage-competitors", methods=["GET"])
def manage_competitors_page():
    """Renders the competitor management page."""
    all_competitors = db.query(Competitor).order_by(Competitor.id.desc()).all()
    return render_template("manage_competitors.html", competitors=all_competitors)

@app.route("/competitors/add", methods=["POST"])
def add_competitor():
    """Adds a new competitor to the database."""
    url = request.form.get("url")
    instagram = request.form.get("instagram_username")

    if not url and not instagram:
        # Add a flash message for error
        return redirect(url_for("manage_competitors_page"))

    new_competitor = Competitor(url=url, instagram_username=instagram)
    db.add(new_competitor)
    db.commit()

    # Add a flash message for success
    return redirect(url_for("manage_competitors_page"))

@app.route("/competitors/delete/<int:competitor_id>")
def delete_competitor(competitor_id):
    """Deletes a competitor from the database."""
    competitor = db.query(Competitor).get(competitor_id)
    if competitor:
        # Also delete related analysis results to maintain integrity
        db.query(AnalysisResult).filter_by(competitor_id=competitor.id).delete()
        db.delete(competitor)
        db.commit()
        # Add a flash message
    return redirect(url_for("manage_competitors_page"))

if __name__ == "__main__":
    # This block is now for direct execution via `python app/web_app.py`
    # The `init_db` is called via the `before_request` hook.
    app.run(debug=True, host='0.0.0.0', port=5000)
