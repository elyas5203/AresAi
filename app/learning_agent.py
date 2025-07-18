import requests
import json
import uuid
from app.database import SessionLocal
from app.models import Conversation

class LearningAgent:
    def __init__(self, ollama_base_url="http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.db = SessionLocal()
        self.session_id = str(uuid.uuid4()) # Create a unique ID for this conversation session

    def _load_history(self):
        """Loads conversation history for the current session from the DB."""
        history = self.db.query(Conversation).filter(Conversation.session_id == self.session_id).order_by(Conversation.timestamp).all()
        return [{"role": h.role, "content": h.content} for h in history]

    def _save_message(self, role, content):
        """Saves a message to the conversation history in the DB."""
        message = Conversation(
            session_id=self.session_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()

    def chat(self, user_input, model="llama3"):
        """
        Sends a message to the Llama3 model and gets a response,
        while maintaining history in the database.
        """
        self._save_message("user", user_input)
        conversation_history = self._load_history()

        api_url = f"{self.ollama_base_url}/api/chat"
        payload = {
            "model": model,
            "messages": conversation_history
        }

        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line)
                        full_response += json_line.get("message", {}).get("content", "")
                        if json_line.get("done"):
                            break
                    except json.JSONDecodeError:
                        print(f"Could not decode json line: {line}")

            self._save_message("assistant", full_response)
            return full_response

        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return "Sorry, I'm having trouble connecting to my brain."

    def get_advice(self, competitor_analysis_results):
        """
        Generates business advice based on competitor analysis.
        """
        prompt = "Based on the following analysis of my competitors, please provide some actionable advice for my luxury stationery business:\n\n"
        for result in competitor_analysis_results:
            prompt += f"- {result.competitor.url}: {result.description}\n"

        prompt += "\nWhat are some creative marketing ideas or product improvements I could make?"

        return self.chat(prompt)

if __name__ == '__main__':
    agent = LearningAgent()
    print(f"Starting new chat session: {agent.session_id}")

    print("AI Assistant: Hello! How can I help you today?")
    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit"]:
            break

        ai_response = agent.chat(user_message)
        print(f"AI Assistant: {ai_response}")
