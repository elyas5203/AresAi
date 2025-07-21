import requests
import json
import uuid
import base64
from app.database import SessionLocal
from app.models import Conversation

class LearningAgent:
    def __init__(self, ollama_base_url="http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.db = SessionLocal()
        self.session_id = str(uuid.uuid4())
        self.system_prompt = {
            "role": "system",
            "content": """
            تو یک دستیار هوش مصنوعی به نام 'چی‌چی' هستی که برای یک فروشگاه آنلاین لوازم تحریر لوکس و فانتزی به نام 'تحریرچی‌شاپ' کار می‌کنی. شخصیت تو ترکیبی از یک استراتژیست بازاریابی خلاق، یک تحلیل‌گر داده‌ی باهوش و یک دوست صمیمی و شوخ‌طبع است.

            **قوانین اصلی:**
            1.  **زبان:** فقط و فقط به زبان فارسی صحبت کن. لحنت باید کاملاً محاوره‌ای، خودمونی و گاهی بامزه باشه. از کلمات کتابی و رسمی پرهیز کن.
            2.  **خلاقیت:** همیشه به دنبال ایده‌های نو و خلاقانه باش. به جای جواب‌های کلیشه‌ای، راهکارهای خاص و جسورانه پیشنهاد بده.
            3.  **تحلیل‌گری:** وقتی ازت خواسته می‌شه چیزی رو تحلیل کنی (مثل یک وب‌سایت یا یک عکس)، مثل یک کارآگاه دقیق باش. به جزئیات توجه کن و نکات مثبت و منفی رو با دلیل و مدرک بیان کن.
            4.  **شخصیت:** تو عاشق لوازم تحریر هستی و این علاقه باید در حرفات مشخص باشه. از مثال‌های مرتبط با دنیای رنگارنگ دفتر و مداد استفاده کن.
            5.  **هدف نهایی:** یادت نره که هدف اصلی تو کمک به رشد 'تحریرچی‌شاپ' و افزایش فروش اونه. تمام مشاوره‌هات باید در راستای این هدف باشه.

            **مثال شروع گفتگو:**
            "سلام رفیق! چی‌چی هستم، دستیار همیشگی تو در دنیای رنگی 'تحریرچی‌شاپ'. امروز چه نقشه‌ای برای ترکوندن بازار داری؟"
            """
        }

    def _load_history(self):
        """Loads conversation history for the current session from the DB."""
        history = self.db.query(Conversation).filter(Conversation.session_id == self.session_id).order_by(Conversation.timestamp).all()
        messages = [self.system_prompt]
        messages.extend([{"role": h.role, "content": h.content} for h in history])
        return messages

    def _save_message(self, role, content):
        """Saves a message to the conversation history in the DB."""
        message = Conversation(
            session_id=self.session_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()

    def chat(self, user_input, model="llama3", image_data=None):
        """
        Sends a message (and optionally an image) to the Llama3 model and gets a response.
        """
        # Prepare the user message
        user_message = {"role": "user", "content": user_input}
        if image_data:
            # Add image to the message if present (for multimodal models)
            user_message["images"] = [image_data]

        # Save only the text part to DB to avoid storing large image data
        self._save_message("user", user_input)

        # Load full history including the new message
        conversation_history = self._load_history()
        conversation_history.append(user_message)

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
            return "ای وای! انگار یه مشکلی پیش اومده و نمی‌تونم به مغزم وصل بشم. یه چند لحظه دیگه دوباره امتحان کن."

    def analyze_image(self, user_prompt, image_path, model="llava"):
        """
        Analyzes an image using a multimodal model like Llava.
        The image_path is the path to the image file.
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Use the chat method to send the image and prompt
            # Make sure the 'model' parameter is a multimodal model you have, like 'llava'
            return self.chat(user_prompt, model=model, image_data=encoded_string)

        except Exception as e:
            print(f"Error analyzing image: {e}")
            return "شرمنده، نتونستم عکس رو تحلیل کنم. فایلش مشکلی نداشت؟"

    def get_advice(self, competitor_analysis_results):
        """
        Generates business advice based on competitor analysis.
        """
        if not competitor_analysis_results:
            return "هیچ تحلیلی برای ارائه مشاوره وجود نداره. اول باید چندتا از رقبامون رو تحلیل کنیم."

        prompt = "بر اساس تحلیل‌های زیر از رقبای من، چندتا راهکار عملی و خلاقانه برای کسب و کار لوازم تحریر لوکس من پیشنهاد بده:\n\n"
        for result in competitor_analysis_results:
            # Check if the result object has a competitor relationship
            if hasattr(result, 'competitor') and result.competitor:
                prompt += f"- وب‌سایت: {result.competitor.url}\n  توضیحات: {result.description}\n\n"
            else:
                prompt += f"- تحلیل بدون مشخصات رقیب: {result.description}\n\n"

        prompt += "\nایده‌های جدید برای بازاریابی، محصولات جدید، یا بهبود وب‌سایت چی داری؟ خیلی خودمونی و واضح بگو."

        return self.chat(prompt)

    def suggest_hashtags(self, caption, image_path=None):
        """
        Suggests relevant and trending hashtags for an Instagram post.
        """
        prompt = f"""
        برای یک پست اینستاگرام با کپشن زیر، یک لیست از 20 هشتگ مناسب پیشنهاد بده. هشتگ‌ها باید ترکیبی از هشتگ‌های عمومی، تخصصی و مرتبط با برند 'تحریرچی‌شاپ' باشن.

        **کپشن:**
        "{caption}"

        لطفاً هشتگ‌ها را در یک خط و با فاصله از هم، بدون هیچ توضیح اضافه‌ای، فقط به صورت `#هشتگ1 #هشتگ2` برگردون.
        """

        image_data = None
        if image_path:
            try:
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
            except Exception as e:
                print(f"Could not read image for hashtag suggestion: {e}")

        # Use a powerful model for creative tasks like this
        return self.chat(prompt, model="llama3", image_data=image_data)


if __name__ == '__main__':
    agent = LearningAgent()
    print(f"Starting new chat session: {agent.session_id}")

    # Example image analysis:
    # Make sure you have a model like 'llava' by running 'ollama pull llava'
    # And have an image file named 'test_image.jpg'
    # with open("test_image.jpg", "w") as f: f.write("dummy") # Create a dummy file for testing
    # advice = agent.analyze_image("این پست اینستاگرام رو تحلیل کن و بگو چطور می‌تونم بهترش کنم.", "test_image.jpg")
    # print(f"\n--- Image Analysis Advice ---\n{advice}")

    print("AI Assistant: سلام! من چی‌چی هستم. چه کمکی از دستم برمیاد؟")
    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit"]:
            break

        ai_response = agent.chat(user_message)
        print(f"AI Assistant: {ai_response}")
